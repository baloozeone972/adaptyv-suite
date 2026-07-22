"""adaptyv-kinetics — read the binding data package, re-fit, QC, and report."""

from adaptyv_kinetics.io.package import DataPackage
from adaptyv_kinetics.io.synthetic import PackageGenerator
from adaptyv_kinetics.schemas import KineticFit, QCFlag, Trace, TraceVerdict

__all__ = [
    "DataPackage",
    "KineticFit",
    "PackageGenerator",
    "QCFlag",
    "Trace",
    "TraceVerdict",
]
__version__ = "0.0.1"
