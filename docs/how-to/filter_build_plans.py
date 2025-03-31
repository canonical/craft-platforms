from typing import Iterable, Sequence
from craft_platforms import BuildInfo, DistroBase, DebianArchitecture

build_plan = [
    BuildInfo(
        platform="laptop",
        build_for=DebianArchitecture.AMD64,
        build_on=DebianArchitecture.AMD64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
    BuildInfo(
        platform="laptop",
        build_for=DebianArchitecture.AMD64,
        build_on=DebianArchitecture.RISCV64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
    BuildInfo(
        platform="laptop",
        build_for=DebianArchitecture.AMD64,
        build_on=DebianArchitecture.I386,
        build_base=DistroBase("debian", "12"),
    ),
    BuildInfo(
        platform="laptop",
        build_for=DebianArchitecture.AMD64,
        build_on=DebianArchitecture.RISCV64,
        build_base=DistroBase("ubuntu", "4.10"),
    ),
    BuildInfo(
        platform="nostalgia",
        build_for=DebianArchitecture.I386,
        build_on=DebianArchitecture.I386,
        build_base=DistroBase("windows", "5"),
    ),
    BuildInfo(
        platform="phone",
        build_for=DebianArchitecture.ARM64,
        build_on=DebianArchitecture.S390X,
        build_base=DistroBase("ubuntu", "22.04"),
    ),
    BuildInfo(
        platform="phone",
        build_for=DebianArchitecture.ARM64,
        build_on=DebianArchitecture.RISCV64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
    BuildInfo(
        platform="jpeg",
        build_for="all",
        build_on=DebianArchitecture.I386,
        build_base=DistroBase("debian", "12"),
    ),
    BuildInfo(
        platform="jpeg",
        build_for="all",
        build_on=DebianArchitecture.AMD64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
    BuildInfo(
        platform="jpeg",
        build_for="all",
        build_on=DebianArchitecture.I386,
        build_base=DistroBase("sunos", "4"),
    ),
]
# :docs:end_build_plan


def filter_build_plan(exhaustive_build_plan):
    """Filter the build plan to only include Ubuntu runners."""
    return [
        info
        for info in exhaustive_build_plan
        if info.build_base.distribution == "ubuntu"
    ]
    # :docs:end_filter


ubuntu_only_build_plan = [
    BuildInfo(
        platform="laptop",
        build_for=DebianArchitecture.AMD64,
        build_on=DebianArchitecture.AMD64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
    BuildInfo(
        platform="laptop",
        build_for=DebianArchitecture.AMD64,
        build_on=DebianArchitecture.RISCV64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
    BuildInfo(
        platform="laptop",
        build_for=DebianArchitecture.AMD64,
        build_on=DebianArchitecture.RISCV64,
        build_base=DistroBase("ubuntu", "4.10"),
    ),
    BuildInfo(
        platform="phone",
        build_for=DebianArchitecture.ARM64,
        build_on=DebianArchitecture.S390X,
        build_base=DistroBase("ubuntu", "22.04"),
    ),
    BuildInfo(
        platform="phone",
        build_for=DebianArchitecture.ARM64,
        build_on=DebianArchitecture.RISCV64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
    BuildInfo(
        platform="jpeg",
        build_for="all",
        build_on=DebianArchitecture.AMD64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
]
# :docs:end_filtered_build_plan
for left, right in zip(filter_build_plan(build_plan), ubuntu_only_build_plan):
    assert left == right, (left, right)

oldest_with_riscv_preference = [
    BuildInfo(
        platform="laptop",
        build_for=DebianArchitecture.AMD64,
        build_on=DebianArchitecture.RISCV64,
        build_base=DistroBase("ubuntu", "4.10"),
    ),
    BuildInfo(
        platform="phone",
        build_for=DebianArchitecture.ARM64,
        build_on=DebianArchitecture.RISCV64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
    BuildInfo(
        platform="jpeg",
        build_for="all",
        build_on=DebianArchitecture.AMD64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
]
# :docs:end_oldest_with_riscv_preference

native_only_prefer_amd64 = [
    BuildInfo(
        platform="laptop",
        build_for=DebianArchitecture.AMD64,
        build_on=DebianArchitecture.AMD64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
    BuildInfo(
        platform="jpeg",
        build_for="all",
        build_on=DebianArchitecture.AMD64,
        build_base=DistroBase("ubuntu", "24.04"),
    ),
]
# :docs:end_native_only_prefer_amd64
