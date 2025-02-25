"""Common and helpful assertion methods a la Vitest, Jest, or JUnit"""


def assertIsNone(someVar):
    assert someVar is None


def assertIsNotNone(someVar):
    assert someVar is not None


def assertIsEmpty(someSequence):
    assert len(someSequence) == 0


def assertHasLengthOf(someSequence, length):
    assert len(someSequence) == length
