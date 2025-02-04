// SPDX-License-Identifier: GPL-2.0
//! Test of a standalone module with a single .rs file.

use kernel::prelude::*;

mod my_module;
use my_module::module_fun;

module! {
    type: TestRustModule,
    name: "test_rust_module",
    author: "Hong, Yifan <elsk@google.com>",
    description: "Test Rust module",
    license: "GPL",
}

struct TestRustModule {}

impl kernel::Module for TestRustModule {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        module_fun();
        Ok(TestRustModule {})
    }
}
