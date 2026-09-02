<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/dist/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/dist/hero-light.svg">
  <img src="assets/dist/hero-light.svg" width="880" alt="My loss function in life is feeling alive.">
</picture>

My loss function in life is feeling alive.

I run [Immovable Tech](https://immovabletech.com). Before that I spent eight years putting models into products that already had users — search, KYC, roofs measured from the air, assistants that had to answer in two languages. I care about the part after the demo: latency, evals, the bill, whether it still works on a Monday.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/dist/act-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/dist/act-light.svg">
  <img src="assets/dist/act-light.svg" width="880" alt="See, choose, act — AI that acts, not just answers.">
</picture>

## Work

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/dist/work-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/dist/work-light.svg">
  <img src="assets/dist/work-light.svg" width="880" alt="+50% CTR on catalog search. Aerial line detection 28% to 59%. CES 2019 live demo.">
</picture>

1. **Immovable Tech** — Agents that run the loop, not the slide. LangGraph + LangSmith, graph + vector RAG, models tuned on the domain, evals you can read later.
2. **Catalog search at 5,000 QPS** — Semantic matching and learn-to-rank. Click-through +50%, revenue +10%, Milvus underneath.
3. **Roofs from the air** — Line detection 28% → 59%. Facets at 86% mIOU. Triton + INT8, 25% faster, 30% less VRAM.
4. **A national-scale assistant** — English and Hinglish, thousands of chats a day. The KYC face stack next to it cut manual review about 25%.
5. **OCR that beat the API I was paying for** — +12% on ICDAR 2013 versus Google Vision, at a tenth the infra. BERT on the correction pass.
6. **CES 2019** — Gesture, face, collision tracking in a live golf-cart demo. The [public repo](https://github.com/iamrishab/artificial-intelligence-conductor) is a dummy sketch, not the show build.

<details>
<summary>How the later agent work is shaped</summary>

Questions become DAGs. Known SQL hits a template; the model only writes when nothing matches. Read-only, retries. Judges and a small red team sit in front of the user. When a form bot has to die, the new tools run beside it until they match.

</details>

## How I take work

I take 0→1 AI products and the messy ones that already exist. Discovery through deploy. If you need a deck, I’m the wrong person. If you need a system that is still correct in six months, [email me](mailto:rishabpal.work@gmail.com).

## Stack

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/dist/stack-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/dist/stack-light.svg">
  <img src="assets/dist/stack-light.svg" width="880" alt="Agents, models, data, serve, eval.">
</picture>

LangGraph · LangSmith · PyTorch · RAG (Neo4j / Milvus / Pinecone) · FastAPI · Triton · AWS / GCP / Azure

<details>
<summary>The rest of the bench</summary>

- Agents: LangGraph, LangSmith, LangChain, CrewAI, MCP, OpenAI Agents SDK
- Models: PyTorch, Transformers, LoRA / PEFT, Llama, Stable Diffusion / FLUX
- Retrieve: Neo4j, Milvus, Pinecone
- Serve: FastAPI, Docker, ONNX, TensorRT, NVIDIA Triton, MLflow
- Cloud: AWS (SageMaker, Lambda, Step Functions), GCP (Cloud Run, Vertex), Azure AI

</details>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/dist/now-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/dist/now-light.svg">
  <img src="assets/dist/now-light.svg" width="880" alt="Now: shipping multi-agent systems with evals and a paper trail">
</picture>

## On the record

Most of the work above is closed. What I can show: a [Differentiable Binarization implementation](https://github.com/iamrishab/DB-tf), an [OpenVINO OCR path](https://github.com/iamrishab/openvino-ocr), and a [local LangGraph assistant](https://github.com/iamrishab/private-personal-proxy). The CES cart has a [dummy sketch](https://github.com/iamrishab/artificial-intelligence-conductor), not the show build. I used to answer [face-embedding questions](https://stackoverflow.com/questions/61302918/best-metric-for-face-embedding-comparison-during-inference) on Stack Overflow.

rishabpal.work@gmail.com · [LinkedIn](https://linkedin.com/in/rishabpal) · [Immovable Tech](https://immovabletech.com)
