# Scale Estimation Literature Review - GitHub Pages

This is the documentation site for the comprehensive literature review on **Single & Multi-View Scale and Size Estimation**.

## Live Site

Once deployed to GitHub Pages: `https://alinikkhah2001.github.io/size-scale-estimation/`

## Local Development

```bash
cd docs
bundle install
bundle exec jekyll serve
# Open http://localhost:4000
```

## Structure

```
docs/
├── _config.yml           # Jekyll configuration
├── _layouts/
│   └── default.html      # Main layout
├── assets/css/
│   └── style.css         # Custom styling
├── index.md              # Main review article
├── methods/index.md      # Methods taxonomy
├── models/index.md       # Model zoo with specs
├── datasets/index.md     # Benchmark datasets
├── benchmarks/index.md   # Leaderboards & results
├── applications/index.md # Use cases by domain
└── camera-geometry.md    # Camera geometry fundamentals
```

## Content Overview

| Page | Description |
|------|-------------|
| **Main Review** | 40+ page survey covering 4 method families, 50+ papers, 20+ datasets |
| **Methods** | Taxonomy with decision tree and hybrid pipelines |
| **Models** | 15+ model cards with specs, code snippets, links |
| **Datasets** | 30+ datasets with access instructions |
| **Benchmarks** | Leaderboards for NYU, KITTI, DA-2K, Omni3D |
| **Applications** | 8 domains × use cases with implementation patterns |
| **Camera Geometry** | Focal length, intrinsics, coordinate systems, error analysis |

## Deployment

1. Push to `main` branch
2. Enable GitHub Pages in repository settings
3. Source: `Deploy from branch` → `main` → `/docs`
4. Site builds automatically via GitHub Actions

## License

MIT License - see [LICENSE](../LICENSE)

## Citation

If you use this review in your research:

```bibtex
@misc{size_scale_estimation_review_2025,
  title={Single \& Multi-View Scale Estimation: A Comprehensive Literature Review},
  author={Research Team},
  year={2025},
  url={https://github.com/AliNikkhah2001/size-scale-estimation}
}
```