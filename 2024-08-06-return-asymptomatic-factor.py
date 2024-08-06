def get_asymptomatic_factor():
    # https://doi.org/10.1371/journal.pone.0270694
    long_2020_asymptomatic_delta = 0  # "The initial CT values for 37 asymptomatic individuals and 37 symptomatic patients appeared similar" https://www.nature.com/articles/s41591-020-0965-6
    lee_2020_asymptomatic_delta = 0  # "There were no significant differences in CT values between asymptomatic and symptomatic (including presymptomatic) patients." 10.1001/jamainternmed.2020.3862
    yang_2023_asymptomatic_delta = 0.99  # Extracted from supplement figure 4D https://doi.org/10.1016/S2666-5247(23)00139-8

    hall_asymptomatic_ct_median = 29.9
    hall_symptomatic_ct_median = 21.8
    hall_asymptomatic_delta = (
        hall_asymptomatic_ct_median - hall_symptomatic_ct_median
    )
    ASYMPTOMATIC_ADJUSTMENT_FACTOR = (
        hall_asymptomatic_delta
        + long_2020_asymptomatic_delta
        + lee_2020_asymptomatic_delta
        + yang_2023_asymptomatic_delta
    ) / 4

    return ASYMPTOMATIC_ADJUSTMENT_FACTOR


ASYMPTOMATIC_ADJUSTMENT_FACTOR = get_asymptomatic_factor()
print(ASYMPTOMATIC_ADJUSTMENT_FACTOR)
