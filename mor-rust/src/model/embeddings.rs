use tch::{nn, Tensor};
use tch::nn::Module;

#[derive(Debug)]
pub struct EmbeddingLayer {
    embeddings: nn::Embedding,
}

impl EmbeddingLayer {
    pub fn new(vs: &nn::Path, vocab_size: i64, embedding_dim: i64) -> Self {
        let embeddings = nn::embedding(vs, vocab_size, embedding_dim, Default::default());
        Self { embeddings }
    }
}

impl Module for EmbeddingLayer {
    fn forward(&self, input: &Tensor) -> Tensor {
        self.embeddings.forward(input)
    }
}
