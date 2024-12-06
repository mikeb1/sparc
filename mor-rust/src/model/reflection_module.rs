use tch::{nn, Tensor};
use tch::nn::Module;

pub struct ReflectionModule {
    linear1: nn::Linear,
    linear2: nn::Linear,
}

impl ReflectionModule {
    pub fn new(vs: &nn::Path, embedding_dim: i64, hidden_dim: i64, _num_layers: i64) -> Self {
        let linear1 = nn::linear(vs / "linear1", embedding_dim, hidden_dim, Default::default());
        let linear2 = nn::linear(vs / "linear2", hidden_dim, embedding_dim, Default::default());
        Self { linear1, linear2 }
    }
}

impl Module for ReflectionModule {
    fn forward(&self, input: &Tensor) -> Tensor {
        let hidden = input.apply(&self.linear1).relu();
        hidden.apply(&self.linear2)
    }
}
