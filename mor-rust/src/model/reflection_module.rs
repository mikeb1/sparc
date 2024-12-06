use tch::{nn, Tensor};

pub struct ReflectionModule {
    transformer: nn::TransformerEncoder,
}

impl ReflectionModule {
    pub fn new(vs: &nn::Path, embedding_dim: i64, num_heads: i64, num_layers: i64) -> Self {
        let config = nn::transformer::TransformerEncoderConfig {
            d_model: embedding_dim,
            nhead: num_heads,
            num_encoder_layers: num_layers,
            dim_feedforward: embedding_dim * 4,
            dropout: 0.1,
            activation: nn::transformer::Activation::Gelu,
            ..Default::default()
        };
        let transformer = nn::transformer::transformer_encoder(vs, config);
        Self { transformer }
    }

    pub fn forward(&self, input: &Tensor) -> Tensor {
        self.transformer.forward(input)
    }
}
