// SPDX-License-Identifier: GPL-2.0
//! Test of a standalone module with a single .rs file.

use kernel::prelude::*;

module! {
    type: TestStandaloneRustModule,
    name: "test_standalone_rust_module",
    author: "Hong, Yifan <elsk@google.com>",
    description: "Test of a standalone module with a single .rs file.",
    license: "GPL",
}

struct TestStandaloneRustModule {}

impl kernel::Module for TestStandaloneRustModule {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        Ok(TestStandaloneRustModule {})
    }
}
