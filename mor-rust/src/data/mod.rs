pub mod dataset;

use tch::Tensor;

pub struct Batch {
    pub inputs: Tensor,
    pub targets: Tensor,
}

pub trait DataLoader {
    fn next_batch(&mut self) -> Option<Batch>;
    fn reset(&mut self);
}
