mod config;
mod utils;
mod data;
mod model;

use log::info;
use structopt::StructOpt;
use anyhow::Result;

#[derive(StructOpt, Debug)]
#[structopt(name = "Mixture of Reflection (MoR)")]
struct Opt {
    /// Flag to start training the model
    #[structopt(long)]
    train: bool,

    /// Flag to evaluate the model
    #[structopt(long)]
    evaluate: bool,

    /// Flag to run inference with the model
    #[structopt(long)]
    inference: bool,

    /// Path to configuration file
    #[structopt(long, default_value = "config.json")]
    config: String,
}

fn main() -> Result<()> {
    env_logger::init();

    let opt = Opt::from_args();
    let config_path = opt.config;
    let cfg = config::Config::from_file(&config_path)?;

    if opt.train {
        info!("Starting training...");
        model::train::train(&cfg)?;
    } else if opt.evaluate {
        info!("Evaluating the model...");
        model::evaluate::evaluate(&cfg)?;
    } else if opt.inference {
        info!("Running inference...");
        // Add inference logic here
    } else {
        info!("No action specified. Use --train, --evaluate, or --inference.");
    }

    Ok(())
}
