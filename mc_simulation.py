import numpy as np

def MC(sensor, T_hr, dt_sec, dt_hr, N, MC_runs):
    np.random.seed(42) # fixed seed for reproducibility
    theta_final = np.zeros(MC_runs)
    for m in range(MC_runs):
        # Constant bias error
        bias = sensor['b'] * np.random.randn()
        theta_bias = bias * T_hr

        # Angular Random Walk (white noise)
        rate_noise = sensor['ARW'] * np.random.randn(N) / np.sqrt(dt_hr)
        theta_arw = np.sum(rate_noise) * dt_hr

        # Bias Instability (Gauss-Markov process)
        tau = sensor['tau']
        phi = np.exp(-dt_sec / tau)
        sigma_b = sensor['BI'] * np.sqrt(2 * np.log(2) / np.pi)
        sigma_w = sigma_b * np.sqrt(1 - phi**2)
        b = np.zeros(N)
        b[0] = sigma_b * np.random.randn()
        for k in range(1, N):
            b[k] = phi * b[k-1] + sigma_w * np.random.randn()
        theta_bi = np.sum(b) * dt_hr

        # Total error
        theta_total = theta_bias + theta_arw + theta_bi
        theta_final[m] = theta_total

    theta_RMS = np.sqrt(np.mean(theta_final**2))
    return theta_RMS
