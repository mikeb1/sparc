use crate::config::Config;
use crate::data::{DataLoader, dataset::ExampleDataLoader};
use crate::model::{
    embeddings::EmbeddingLayer,
    expert_selector::ExpertSelector,
    reflection_module::ReflectionModule,
    integration_layer::IntegrationLayer,
};
use anyhow::Result;
use tch::{nn, Device, no_grad};
use log::info;

pub fn evaluate(cfg: &Config) -> Result<()> {
    let device = Device::Cpu; // Change to Device::Cuda(0) if GPU is available

    // Initialize variable stores and load saved parameters
    let vs = nn::VarStore::new(device);
    vs.load(&cfg.model_save_path)?;
    let root = vs.root();

    // Model components parameters (should match those used in training)
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

    // DataLoader
    let mut data_loader = ExampleDataLoader::new(&cfg.data_path, cfg.batch_size);

    // Evaluation Loop
    let mut total_correct = 0;
    let mut total_samples = 0;

    no_grad(|| {
        while let Some(batch) = data_loader.next_batch() {
            let inputs = batch.inputs.to_device(device);
            let targets = batch.targets.to_device(device);

            // Forward Pass
            let embedded = embeddings.forward(&inputs);
            let expert_probs = selector.forward(&embedded.mean_dim(&[embedded.size()[1]-1], false, tch::Kind::Float));

            let mut expert_outputs = Vec::with_capacity(cfg.num_experts);
            for (i, expert) in experts.iter().enumerate() {
                let prob = expert_probs.select(1, i as i64).unsqueeze(-1).unsqueeze(-1);
                let output = expert.forward(&embedded);
                expert_outputs.push(output * prob);
            }

            let predictions = integrator.forward(&expert_outputs, &expert_probs);

            // Compute accuracy
            let predicted_classes = predictions.argmax(-1, false);
            let correct = predicted_classes.eq_tensor(&targets).sum(tch::Kind::Int64);
            total_correct += i64::from(&correct);
            total_samples += inputs.size()[0];
        }
    });

    let accuracy = total_correct as f64 / total_samples as f64 * 100.0;
    info!("Evaluation Accuracy: {:.2}%", accuracy);

    Ok(())
}
