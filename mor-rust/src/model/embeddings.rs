use tch::{nn, Tensor};

pub struct EmbeddingLayer {
    embeddings: nn::Embedding,
}

impl EmbeddingLayer {
    pub fn new(vs: &nn::Path, vocab_size: i64, embedding_dim: i64) -> Self {
        let embeddings = nn::embedding(vs, vocab_size, embedding_dim, Default::default());
        Self { embeddings }
    }

    pub fn forward(&self, input: &Tensor) -> Tensor {
        self.embeddings.forward(input)
    }
}
