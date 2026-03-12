**Rand int error**
*soln*<b> :</b>

This is a classic Monte Carlo issue — the results vary between runs because the simulation uses random numbers, so each run gives slightly different RMS values. This is expected statistical behaviour, but there are two ways to fix it depending on what you want:Here's what each option means:



Fixed seed — np.random.seed(42) at the start of every MC run. Same inputs → identical output every time. Fast, deterministic. Best if you want reproducibility.

More MC runs — increase from 500 → 5000+ runs. The law of large numbers kicks in and the RMS converges to a stable value. Slightly slower but statistically rigorous.

Both — deterministic AND statistically robust. Recommended for engineering use.

def MC(sensor, T\_hr, dt\_sec, dt\_hr, N, MC\_runs):

&nbsp;   np.random.seed(42)


**diameter error :**



