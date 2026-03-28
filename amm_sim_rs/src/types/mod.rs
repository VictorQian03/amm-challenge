//! Core types for the simulation engine.

pub mod config;
pub mod result;
pub mod trade_info;
pub mod wad;

pub use config::SimulationConfig;
pub use result::{BatchSimulationResult, LightweightSimResult, LightweightStepResult};
pub use trade_info::TradeInfo;
pub use wad::Wad;
