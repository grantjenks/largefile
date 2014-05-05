"""
# Large File Support
"""

import os, tempfile, random

from cStringIO import StringIO
from itertools import imap, chain
from multiprocessing import Pool

def sizes(filename, bufsize=2**22):
    """
    Compute sizes for `filename` to read at newline boundaries.
    Sizes will be approximately `bufsize`.
    """
    reads = []

    with open(filename, 'rb') as fptr:
        while True:
            fptr.seek(bufsize, 1)
            line = fptr.readline()
            if line:
                pos = fptr.tell()
                reads.append(pos)
            else:
                break

    pos = os.path.getsize(filename)
    reads.append(pos)

    for pos in reversed(xrange(1, len(reads))):
        reads[pos] = reads[pos] - reads[pos - 1]

    return reads

def chunks(filename, bufsize=2**22):
    """
    Generator for text chunks from `filename`.
    Chunks aligned to newline boundaries and of approximately `bufsize`.
    """
    reads = sizes(filename, bufsize)
    with open(filename, 'rb') as fptr:
        for chunk in imap(fptr.read, reads):
            yield chunk

def lines(filename, bufsize=2**22):
    """
    Generator for lines from `filename`.
    Buffers reads of approximately `bufsize`.
    """
    for chunk in chunks(filename, bufsize):
        for line in StringIO(chunk):
            yield line

def linecount(filename, bufsize=2**22):
    """
    Line count for `filename`.
    Buffers reads of approximately `bufsize`.
    """
    return sum(chunk.count('\n') for chunk in chunks(filename, bufsize))

def sort(filename, readchunk=2**28, writechunk=2**18):
    """
    Sort `filename` *in-place*.
    Buffers reads of approximately `readchunk` size.
    Buffers writes of approximately `writechunk` size.
    """
    total, args, files = 0, [], []
    reads = sizes(filename, readchunk)

    try:
        for size in reads:
            files.append(tempfile.mktemp(prefix='largefile-'))
            args.append((filename, total, size, files[-1]))
            total += size

        pool = Pool()
        pool.map(_sort_worker, args, 1)
        pool.close()

        with open(filename, 'wb') as fptr:
            readers = [chunks(filename, writechunk) for filename in files]
            while True:
                reads = (StringIO(reader.next()) for reader in readers)
                lines = sorted(chain.from_iterable(reads))
                if len(lines) == 0: break
                fptr.writelines(lines)
    finally:
        for name in files:
            try:
                os.remove(name)
            except:
                pass

def _sort_worker(args):
    """
    Worker process for `sort` function.
    """
    filename, offset, size, temp = args

    with open(filename, 'rb') as fptr:
        fptr.seek(offset)
        chunk = fptr.read(size)

    lines = sorted(StringIO(chunk))

    with open(temp, 'wb') as fptr:
        fptr.writelines(lines)

def shuffle(filename, readchunk=2**28, writechunk=2**18):
    """
    Shuffle lines in `filename` *in-place*.
    Buffers reads of approximately `readchunk` size.
    Buffers writes of approximately `writechunk` size.
    """
    total, args, files = 0, [], []
    reads = sizes(filename, readchunk)

    try:
        for size in reads:
            files.append(tempfile.mktemp(prefix='largefile-'))
            args.append((filename, total, size, files[-1]))
            total += size

        pool = Pool()
        pool.map(_shuffle_worker, args, 1)
        pool.close()

        with open(filename, 'wb') as fptr:
            readers = [chunks(filename, writechunk) for filename in files]
            while True:
                reads = (StringIO(reader.next()) for reader in readers)
                lines = list(chain.from_iterable(reads))
                random.shuffle(lines)
                if len(lines) == 0: break
                fptr.writelines(lines)
    finally:
        for filename in files:
            try:
                os.remove(filename)
            except:
                pass

def _shuffle_worker(args):
    """
    Worker process for `shuffle` function.
    """
    filename, offset, size, temp = args

    with open(filename, 'rb') as fptr:
        fptr.seek(offset)
        chunk = fptr.read(size)

    lines = list(StringIO(chunk))
    random.shuffle(lines)

    with open(temp, 'wb') as fptr:
        fptr.writelines(lines)

def reduce(filename, generator, bufsize=2**22):
    """
    Reduce lines from `filename` *in-place* using `generator`.

    Reduce will initialize the generator function by calling .next(). Then each
    line from `filename` will be sent to the `generator` and the received line
    will be written back to the file.
    """
    generator.next()
    temp = tempfile.mktemp(prefix='largefile-')
    reader = lines(filename, bufsize)

    with open(temp, 'wb') as fptr:
        for line in reader:
            fptr.write(generator.send(line))

    del reader
    os.remove(filename)
    os.rename(temp, filename)

def uniq2(filename, bufsize=2**22):
    def _uniq():
        last = yield
        yield last
        while True:
            line = yield
            if line != last:
                yield line
            else:
                yield ''
            last = line
    reduce(filename, _uniq, bufsize)

def uniq(filename, bufsize=2**22):
    """
    Remove duplicate lines from `filename` *in-place*.
    Buffers reads of approximately `bufsize`.
    Requires file be sorted.
    """
    temp = tempfile.mktemp(prefix='largefile-')
    reader = lines(filename, bufsize)

    with open(temp, 'wb') as fptr:
        last = reader.next()
        fptr.write(last)
        for line in reader:
            if line != last:
                fptr.write(line)
            last = line

    del reader
    os.remove(filename)
    os.rename(temp, filename)

def apply(filename, func, bufsize=2**22):
    """
    Apply `func` to every line in `filename` *in-place*.
    Buffers reads of approximately `bufsize`.
    """
    temp = tempfile.mktemp(prefix='largefile-')
    reader = lines(filename, bufsize)

    with open(temp, 'wb') as fptr:
        fptr.writelines(func(line) for line in reader)

    del reader
    os.remove(filename)
    os.rename(temp, filename)

def look(filename, needle, key=lambda value: value):
    """
    Return lines where `key(line) == needle` in file.

    Requires file is sorted. Performs a binary search.

    `needle` - value to match
    `key` - function to extract comparison value from line

    >>> parser = lambda val: int(val.split('\t')[0].strip())
    >>> lf.look(63889187, parser)
    ['63889187\t3592559\n', ...]
    """

    start = pos = 0
    end = os.path.getsize(filename)

    with open(filename, 'rb') as fptr:

        # Limit the number of times we binary search.

        for rpt in xrange(50):

            last = pos
            pos = start + ((end - start) / 2)
            fptr.seek(pos)

            # Move the cursor to a newline boundary.

            fptr.readline()

            line = fptr.readline()
            value = key(line)

            if value == needle or pos == last:

                # Seek back until we no longer have a match.

                total = 0
                backoff = 2 ** 5

                try:
                    while True:
                        total += backoff
                        fptr.seek(-backoff, 1)
                        fptr.readline()
                        if needle != key(fptr.readline()):
                            break
                        else:
                            backoff *= 2
                except IOError:
                    fptr.seek(0)

               # Seek forward to the first match.

                for rpt in xrange(total):
                    line = fptr.readline()
                    value = key(line)
                    if needle == value:
                        break
                else:
                    # No needle was found.
                    return []

                results = []

                while value == needle:
                    results.append(line)
                    line = fptr.readline()
                    value = key(line)

                return results

            elif value < needle:
                start = fptr.tell()
            else:
                assert value > needle
                end = fptr.tell()
        else:
            raise RuntimeError('look fail')

class LargeFile:
    def __init__(self, filename):
        self.filename = filename

    def look(self, needle, key=lambda value: value):
        return look(self.filename, needle, key)

    def sort(self):
        sort(self.filename)

    def uniq(self):
        uniq(self.filename)

    def shuffle(self):
        shuffle(self.filename)

    def linecount(self):
        return linecount(self.filename)
