# Local LLMs

The research uses local LLMs to create detection rules. Notably there are 2 different workflows:

1. A Parsing and Classification Workflow that reads through a set of lines in a JSONL file and decides whether they are suspicious/malicious or not. By doing this, a file is created in the form of `malicious_<original_filename>.jsonl`.
   - This file is then used for the AI + Manual approach, where the rules will be created manually from those logs, as well as,
   - Serving as the previous step for the complete AI workflow. This logs are then fed to the `rule_builder` workflow that will decide to create 3 detection rules and 1 correlation. Out of the three detection rules, 2 are picked manually.
2. The `rule_builder` workflow is a set of constraints and instructions on how to successfully create SigmaHQ detection and correlation rules.

## Ollama

Ollama is being used to load and serve local LLMs in my home network. The prompt used to to so is:

```bash
OLLAMA_HOST=0.0.0.0:11434 OLLAMA_CONTEXT_LENGTH=262144 nohup ollama serve > ~/ollama.log 2>&1 &
```

Other `ollama` information:
Commands run on August 3rd.

```bash
$ ollama --version
ollama version is 0.32.2
```

```bash
$ curl http://localhost:11434/api/version
{"version": "0.32.2"}%
```
```bash
$ curl http://localhost:11434/api/tags
curl http://localhost:11434/api/tags | jq
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100   1622 100   1622   0      0  2.41M      0                              0
{
  "models": [
    {
      "name": "gemma4:12b",
      "model": "gemma4:12b",
      "modified_at": "2026-07-24T11:25:05.801177665Z",
      "size": 7556508396,
      "digest": "4eb23ef187e2c5462566d6a1d3bbbc2f1346d0b4327cbb66d58fffbcc9b2b05c",
      "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "gemma4",
        "families": [
          "gemma4"
        ],
        "parameter_size": "11.9B",
        "quantization_level": "Q4_K_M",
        "context_length": 262144,
        "embedding_length": 3840
      },
      "capabilities": [
        "completion",
        "tools",
        "thinking",
        "vision"
      ]
    },
  ]
}
```


## Gemma4:12b Configuration in scripts

One of the most difficult decision was to chose one or more llms for these processes. Initially, the models chosen were:

- Gemma4:e4b for the `parsing_and_classification` workflow.
- Gemma4:12b for the `rule_builder` workflow.

However, after prior-to-experimentation testing, the difference in speed between the `e4b` and the `12b` models was not relevant for the timeline of this research. It takes twice as much time but results seem to be better as the model is 3 times bigger or "smarter".

Other models were considered such as Gemma4:27b and Qwen3.6:27b and Qwen3.6:35b, however, the workflows were one to three orders of magnitude slower due to `tok/s` but also due to the increased reasoning of those models. Often taking over 2 hours for tasks where the 12 billion parameter model Gemma4:12b performed in single-digit minutes.

The premise of this research is whether we can automate detection engineering, not at a grand scale with limited resources but in a local workstation with similar specs of what a detection engineer will have. The environment, the sandbox, the machine learning model, and ultimate the AI workflows can all be run in a computer with a discrete GPU and 16 GiB of RAM. Even without a discrete GPU and a CPU/NPU with 16GiB of RAM.

### Model Specs and Configuration

The model specs are:

The configuration parameters are:

- `parsing_and_classification` workflow:
  - Temperature: 0
  - Context: 16384
  - Full config in [parsing_and_classification.py](../../src/ai_workflows/parsing_and_classification.py)

  ```python
    response: ChatResponse = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False),
            },
        ],
        format="json",
        options={"temperature": 0, "num_ctx": NUM_CTX},
    )
  ```

- `rule_builder` workflow:
  - Temperature: 0
  - Context: 262144
  - Full config in [rule_builder](../../src/ai_workflows/rule_builder.py)
  ```python
    response = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": payload},
        ],
        format="json",
        options={"temperature": 0, "num_ctx": NUM_CTX},
    )
  ```

## Gemma4:12b Model Information

Commands run on August 3rd.

```bash
$ ollama list
NAME            ID              SIZE    MODIFIED
gemma4:12b      4eb23ef187e2    9.6GB   10 days ago
```

```bash
$ ollama show gemma4:12b
  Model
    architecture        gemma4
    parameters          11.9B
    context length      262144
    embedding length    3840
    quantization        Q4_K_M
    requires            0.30.5

  Capabilities
    completion
    vision
    audio
    tools
    thinking

  Projector
    architecture        clip
    parameters          52.38M
    embedding length    3840
    dimensions          3840

  Parameters
    temperature    1
    top_k          64
    top_p          0.95

  License
    Apache License
    Version 2.0, January 2004
    ...
```

```bash
$ ollama show gemma4:12 --modelfile
# Modelfile generated by "ollama show"
# To build a new Modelfile based on this, replace FROM with:
# FROM gemma4:12b

FROM /home/zerodave/.ollama/models/blobs/sha256-1278394b693672ac2799eadc9a83fd98259a6a88a40acfb1dcaa6c6fc895a606
FROM /home/zerodave/.ollama/models/blobs/sha256-675ad6e68101ca9413ec806855c452362f0213f2dfc5800996b086fdb8119842
TEMPLATE {{ .Prompt }}
RENDERER gemma4
PARSER gemma4
PARAMETER temperature 1
PARAMETER top_k 64
PARAMETER top_p 0.95
LICENSE """
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS
"""
```
