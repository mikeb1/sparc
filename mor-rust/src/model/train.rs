use crate::config::Config;
use crate::data::{DataLoader, dataset::ExampleDataLoader};
use crate::model::{
    embeddings::EmbeddingLayer,
    expert_selector::ExpertSelector,
    reflection_module::ReflectionModule,
    integration_layer::IntegrationLayer,
    losses::classification_loss,
};
use anyhow::Result;
use tch::{nn, nn::OptimizerConfig, Device};
use log::info;

pub fn train(cfg: &Config) -> Result<()> {
    let device = Device::Cpu; // Change to Device::Cuda(0) if GPU is available

    // Initialize variable stores
    let vs = nn::VarStore::new(device);
    let root = vs.root();

    // Model components parameters
    let vocab_size = 10000;
    let embedding_dim = 128;
    let hidden_dim = 256;
    let output_dim = 10;
    let num_heads = 8;
    let num_layers = 4;

    let embeddings = EmbeddingLayer::new(&root / "embeddings", vocab_size, embedding_dim);

    let selector = ExpertSelector::new(&root / "selector", embedding_dim, hidden_dim, cfg.num_experts as i64);

    let experts: Vec<ReflectionModule> = (0..cfg.num_experts)
        .map(|i| {
            ReflectionModule::new(
                &root / format!("expert_{}", i),
                embedding_dim,
                num_heads,
                num_layers,
            )
        })
        .collect();

    let integrator = IntegrationLayer::new(&root / "integrator", embedding_dim, output_dim);

    // Optimizer
    let mut optimizer = nn::Adam::default().build(&vs, cfg.learning_rate as f64)?;

    // DataLoader
    let mut data_loader = ExampleDataLoader::new(&cfg.data_path, cfg.batch_size);

    // Training Loop
    for epoch in 1..=cfg.max_epochs {
        info!("Epoch {}/{}", epoch, cfg.max_epochs);
        let mut total_loss = 0.0;
        let mut batches = 0;

        data_loader.reset();

        while let Some(batch) = data_loader.next_batch() {
            let inputs = batch.inputs.to_device(device);
            let targets = batch.targets.to_device(device);

            // Forward Pass
            let embedded = embeddings.forward(&inputs);

            // Expert Selection
            let expert_probs = selector.forward(&embedded.mean_dim(&[embedded.size()[1]-1], false, tch::Kind::Float));

            // Activate Experts
            let mut expert_outputs = Vec::with_capacity(cfg.num_experts);
            for (i, expert) in experts.iter().enumerate() {
                // Determine the probability of selecting this expert
                let prob = expert_probs.select(1, i as i64).unsqueeze(-1).unsqueeze(-1);

                // Expert's output
                let output = expert.forward(&embedded);

                expert_outputs.push(output * prob); // Scale output by selection probability
            }

            // Integration
            let predictions = integrator.forward(&expert_outputs, &expert_probs);

            // Compute Loss
            let loss = classification_loss(&predictions, &targets);

            // Backward Pass and Optimization
            optimizer.zero_grad();
            loss.backward();
            optimizer.step();

            total_loss += f64::from(&loss);
            batches += 1;
        }

        let avg_loss = total_loss / batches as f64;
        info!("Average Loss after epoch {}: {:.4}", epoch, avg_loss);
    }

    // Save the trained model
    vs.save(&cfg.model_save_path)?;

    Ok(())
}
