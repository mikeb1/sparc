use tch::{nn, Tensor, Kind};
use tch::nn::Module;

#[derive(Debug)]
pub struct IntegrationLayer {
    linear: nn::Linear,
}

impl IntegrationLayer {
    pub fn new(vs: &nn::Path, input_dim: i64, output_dim: i64) -> Self {
        let linear = nn::linear(vs / "linear", input_dim, output_dim, Default::default());
        Self { linear }
    }
}

impl Module for IntegrationLayer {
    fn forward(&self, input: &Tensor) -> Tensor {
        input.apply(&self.linear)
    }
}

impl IntegrationLayer {
    pub fn combine_expert_outputs(&self, inputs: &[Tensor], weights: &Tensor) -> Tensor {
        let stacked_inputs = Tensor::stack(inputs, 0);
        let weighted_inputs = weights.unsqueeze(-1).unsqueeze(-1) * stacked_inputs;
        let combined = weighted_inputs.sum1(&[0], false, Kind::Float);
        self.forward(&combined)
    }
}
