use super::{Batch, DataLoader};
use tch::{Tensor, Kind};

pub struct ExampleDataLoader {
    index: usize,
    data: Vec<(Tensor, Tensor)>,
    batch_size: usize,
}

impl ExampleDataLoader {
    pub fn new(_data_path: &str, batch_size: usize) -> Self {
        // For demonstration, create dummy data
        let num_samples = 1000;
        let input_dim = 128;
        let output_dim = 10;

        let inputs = Tensor::rand(&[num_samples, input_dim], (Kind::Float, tch::Device::Cpu));
        let targets = Tensor::randint(output_dim, &[num_samples], (Kind::Int64, tch::Device::Cpu));

        let data = inputs
            .split(1, 0)
            .iter()
            .zip(targets.split(1, 0).iter())
            .map(|(i, t)| (i.squeeze_dim(0), t.squeeze_dim(0)))
            .collect();

        Self {
            index: 0,
            data,
            batch_size,
        }
    }

    pub fn len(&self) -> usize {
        self.data.len()
    }
}

impl DataLoader for ExampleDataLoader {
    fn next_batch(&mut self) -> Option<Batch> {
        if self.index >= self.data.len() {
            return None;
        }

        let end = (self.index + self.batch_size).min(self.data.len());
        let batch_slice = &self.data[self.index..end];

        let inputs: Vec<Tensor> = batch_slice.iter().map(|(i, _)| i.unsqueeze(0)).collect();
        let targets: Vec<Tensor> = batch_slice.iter().map(|(_, t)| t.unsqueeze(0)).collect();

        self.index = end;

        Some(Batch {
            inputs: Tensor::cat(&inputs, 0),
            targets: Tensor::cat(&targets, 0),
        })
    }

    fn reset(&mut self) {
        self.index = 0;
    }
}
