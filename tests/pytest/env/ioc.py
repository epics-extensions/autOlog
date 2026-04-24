"""soft ioc"""
from textwrap import dedent

from caproto.server import PVGroup, PvpropertyEnum, PvpropertyDouble, ioc_arg_parser, pvproperty, run
from caproto.server.records import (
    MbbiFields,
    AiFields,
)
import enum

class EnumDefaultValues(enum.IntEnum):
    zero = 0
    one = 1

class SimpleIOC(PVGroup):
    """
    An IOC with three uncoupled read/writable PVs.

    Scalar PVs
    ----------
    A (int)
    B (float)

    Array PVs
    ---------
    C (array of int)
    """
    intA = pvproperty(
        value=1,
        doc='An integer',
    )

    intB = pvproperty(
        value=1,
        doc='An integer',
    )

    floatA = pvproperty(
        value=2.0,
        dtype=PvpropertyDouble[AiFields],
        record=AiFields,
        )

    floatB = pvproperty(
        value=2.0,
        doc='A float'
    )

    C = pvproperty(
        value=[1, 2, 3],
        doc='An array of integers (max length 3)'
    )

    mbbiA = pvproperty(
        value=EnumDefaultValues.zero,
        dtype=PvpropertyEnum[MbbiFields],
        record=MbbiFields,
        )


if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='simple:',
        desc=dedent(SimpleIOC.__doc__))
    ioc = SimpleIOC(**ioc_options)
    print(ioc.pvdb)
    run(ioc.pvdb, **run_options)