use tch::{nn, Tensor};

pub struct ExpertSelector {
    linear1: nn::Linear,
    linear2: nn::Linear,
}

impl ExpertSelector {
    pub fn new(vs: &nn::Path, input_dim: i64, hidden_dim: i64, num_experts: i64) -> Self {
        let linear1 = nn::linear(vs / "linear1", input_dim, hidden_dim, Default::default());
        let linear2 = nn::linear(vs / "linear2", hidden_dim, num_experts, Default::default());
        Self { linear1, linear2 }
    }

    pub fn forward(&self, input: &Tensor) -> Tensor {
        let hidden = input.apply(&self.linear1).relu();
        let logits = hidden.apply(&self.linear2);
        logits.softmax(-1, tch::Kind::Float)
    }
}
