import itertools


def consume(iterator, n):
    """Advance the iterator n-steps ahead."""
    # Use functions that consume iterators at C speed.
    next(itertools.islice(iterator, n, n), None)