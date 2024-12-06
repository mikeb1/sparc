# Mixture of Reflection (MoR) Model in Rust

This project implements a Mixture of Reflection (MoR) model using Rust and the tch-rs library for PyTorch bindings.

## Prerequisites

- Rust (latest stable version)
- Cargo (comes with Rust)
- LibTorch (PyTorch C++ library)

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd mor-rust
   ```

2. Install LibTorch:
   Download the appropriate version of LibTorch from the official PyTorch website and extract it to a known location.

3. Set up environment variables:
   ```
   export LIBTORCH=<path-to-libtorch>
   export LD_LIBRARY_PATH=${LIBTORCH}/lib:$LD_LIBRARY_PATH
   ```

4. Build the project:
   ```
   cargo build --release
   ```

## Running the Model

To train the model:
```
cargo run --release -- --train
```

To evaluate the model:
```
cargo run --release -- --evaluate
```

You can specify a custom configuration file:
```
cargo run --release -- --train --config custom_config.json
```

## Configuration

The model parameters can be configured in the `config.json` file. Adjust the values as needed for your specific use case.

## Project Structure

- `src/main.rs`: Entry point of the application
- `src/config.rs`: Configuration handling
- `src/data/`: Data loading and processing
- `src/model/`: Model components and training/evaluation logic

## Note

This is a basic implementation and may require further optimization and error handling for production use.
