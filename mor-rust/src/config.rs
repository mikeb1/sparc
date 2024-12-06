use serde::Deserialize;
use std::fs;
use anyhow::Result;

#[derive(Deserialize, Debug, Clone)]
pub struct Config {
    pub learning_rate: f32,
    pub batch_size: usize,
    pub reflection_depth: usize,
    pub num_experts: usize,
    pub max_epochs: usize,
    pub data_path: String,
    pub model_save_path: String,
}

impl Config {
    pub fn from_file(path: &str) -> Result<Self> {
        let content = fs::read_to_string(path)?;
        let cfg: Config = serde_json::from_str(&content)?;
        Ok(cfg)
    }
}
