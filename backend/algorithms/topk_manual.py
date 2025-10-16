"""
Manual Top-K frequent items without Counter/heapq.
We build a frequency dict, then perform a selection routine to extract top K.
"""

def topk_frequent(items, k):
    # Frequency map
    freq = {}
    for x in items:
        if x is None:
            continue
        if x in freq:
            freq[x] += 1
        else:
            freq[x] = 1

    # Convert to list of (item, count)
    pairs = [(item, count) for item, count in freq.items()]

    # Manual partial selection: repeatedly pick max (O(nk))
    k = max(0, int(k))
    result = []
    for _ in range(min(k, len(pairs))):
        # find index of max count
        max_idx = 0
        for i in range(1, len(pairs)):
            if pairs[i][1] > pairs[max_idx][1]:
                max_idx = i
        result.append(pairs[max_idx])
        # remove that element (swap with last then pop for O(1))
        pairs[max_idx], pairs[-1] = pairs[-1], pairs[max_idx]
        pairs.pop()

    return result  # list of (item, count)

# Pseudocode & Complexity
PSEUDOCODE = """
TOPK-FREQUENT(items, k):
  freq <- empty map
  for each x in items:
    if x != None:
      if x in freq: freq[x] <- freq[x] + 1
      else: freq[x] <- 1

  pairs <- list of (item, freq[item]) for each item in freq

  result <- empty list
  repeat min(k, len(pairs)) times:
    max_idx <- 0
    for i from 1 to len(pairs)-1:
      if pairs[i].count > pairs[max_idx].count:
        max_idx <- i
    append pairs[max_idx] to result
    swap pairs[max_idx] with pairs[last]
    remove last from pairs

  return result
"""

COMPLEXITY = "Time: O(n + k*n) ≈ O(nk) in worst case; Space: O(u) where u = unique items."
