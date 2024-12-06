use tch::{nn, Tensor};

pub struct IntegrationLayer {
    linear: nn::Linear,
}

impl IntegrationLayer {
    pub fn new(vs: &nn::Path, input_dim: i64, output_dim: i64) -> Self {
        let linear = nn::linear(vs / "linear", input_dim, output_dim, Default::default());
        Self { linear }
    }

    pub fn forward(&self, inputs: &[Tensor], weights: &Tensor) -> Tensor {
        // Compute weighted sum of expert outputs
        let stacked_inputs = Tensor::stack(inputs, 0); // Shape: [num_experts, batch_size, dim]
        let weighted_inputs = weights.unsqueeze(-1).unsqueeze(-1) * stacked_inputs;
        let combined = weighted_inputs.sum_dim_intlist(&[0], false, tch::Kind::Float); // Sum over experts

        // Apply final transformation
        combined.apply(&self.linear)
    }
}
