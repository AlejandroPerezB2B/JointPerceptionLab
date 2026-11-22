# Publishing on GitHub

1. Create a new GitHub repository named `JointPerceptionLab` (start **private** while reviewing licensing and participant data). Do not initialise it with another README because one is included here.
2. Upload the contents of this folder (not the enclosing ZIP) via GitHub web UI, or use Git:

```bash
git init
git add .
git commit -m "Initial research prototype v0.6 with protocols and Methods draft"
git branch -M main
git remote add origin https://github.com/OWNER/JointPerceptionLab.git
git push -u origin main
```

3. Verify `data/`, `.venv/`, videos and participant files were **not** uploaded.
4. Review `LICENSE_DECISION.md` and `CITATION.cff`; add verified ownership/author metadata and appropriate license before making public.
5. Add GitHub releases for frozen research versions (`v0.6.0` etc.), preserve changelog and tag manuscript-specific releases.
6. Consider archiving a release on Zenodo to obtain a DOI after verifying repository content and permissions.

Never commit raw participant records or unlicensed videos. The default host IP is a lab-specific configuration value; replace it if publishing a reusable public release.
