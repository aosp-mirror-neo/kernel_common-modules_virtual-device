# Copyright (C) 2025 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests on the cflags/aflags/ldflags for kernel_compile_commands()"""

load("@kleaf//build/kernel/kleaf:hermetic_tools.bzl", "hermetic_toolchain")

def _get_workspace_root_impl(subrule_ctx, *, hermetic_tools, _a_source_file):
    """Hack to get workspace root.

    The cflags file is only found below
    workspace_root/bazel-out. This makes the test non-reproducible, but it is
    just a test.

    Don't use this in production!

    Args:
        subrule_ctx: subrule_ctx
        hermetic_tools: from hermetic_toolchain
        _a_source_file: any source file (not generated file)
    """

    # Hack to get workspace root. The cflags file is only found below
    # workspace_root/bazel-out. This makes the test non-reproducible, but it is
    # just a test.
    workspace_root_file = subrule_ctx.actions.declare_file("{}/workspace_root.txt".format(subrule_ctx.label.name))
    command = hermetic_tools.setup + """
        src_real=$(realpath {src})
        echo ${{src_real%{src}}} > {out}
    """.format(
        src = _a_source_file.path,
        out = workspace_root_file.path,
    )
    subrule_ctx.actions.run_shell(
        inputs = [_a_source_file],
        outputs = [workspace_root_file],
        tools = hermetic_tools.deps,
        command = command,
        mnemonic = "CompdbFlagsTestWorkspaceRoot",
    )
    return workspace_root_file

_get_workspace_root = subrule(
    implementation = _get_workspace_root_impl,
    attrs = {
        "_a_source_file": attr.label(
            default = Label("compdb_flags_test.bzl"),
            allow_single_file = True,
        ),
    },
)

def _compdb_flags_test_impl(ctx):
    hermetic_tools = hermetic_toolchain.get(ctx)

    workspace_root_file = _get_workspace_root(hermetic_tools = hermetic_tools)

    script = hermetic_tools.setup + """
        export RUNFILES_DIR=$(realpath .)
        export BUILD_WORKSPACE_DIRECTORY=$(cat {workspace_root_file})
        {test_script} {target}
    """.format(
        test_script = ctx.executable._test_script.short_path,
        target = ctx.executable.target.short_path,
        workspace_root_file = workspace_root_file.short_path,
    )
    script_file = ctx.actions.declare_file("{name}/{name}.sh".format(name = ctx.label.name))
    ctx.actions.write(script_file, script, is_executable = True)
    runfiles = ctx.runfiles([
        script_file,
        workspace_root_file,
    ], transitive_files = hermetic_tools.deps)
    runfiles = runfiles.merge_all([
        ctx.attr._test_script[DefaultInfo].default_runfiles,
        ctx.attr.target[DefaultInfo].default_runfiles,
    ])
    return DefaultInfo(
        files = depset([script_file]),
        executable = script_file,
        runfiles = runfiles,
    )

compdb_flags_test = rule(
    implementation = _compdb_flags_test_impl,
    attrs = {
        "_test_script": attr.label(
            cfg = "exec",
            executable = True,
            default = Label(":compdb_flags_test"),
        ),
        "target": attr.label(
            doc = "the kernel_compile_commands() target",
            executable = True,
            # This is a exec platform executable, but to avoid transition on
            # kernel_build() / ddk_module(), don't apply transitions here.
            cfg = "target",
        ),
    },
    toolchains = [hermetic_toolchain.type],
    subrules = [
        _get_workspace_root,
    ],
    test = True,
)
