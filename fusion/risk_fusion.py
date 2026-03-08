def fuse_scores(cfg_score, beh_score, elve_score, ranges):

    cfg_norm = cfg_score / (ranges["cfg_max"] + 1e-6)
    beh_norm = beh_score / (ranges["beh_max"] + 1e-6)
    elve_norm = elve_score / (ranges["elve_max"] + 1e-6)

    fused = (
        0.35 * cfg_norm +
        0.25 * beh_norm +
        0.40 * elve_norm
    )

    return fused