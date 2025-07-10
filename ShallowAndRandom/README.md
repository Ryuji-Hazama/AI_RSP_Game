# Shallow Learning and Random Guessing AI

The simple shallow learning AI and Random Guessing AI model.

## Table of contents

## About Each Version

### -RSPGame

This is the basic random guessing AI model.

- [RSPGame.py](https://github.com/Ryuji-Hazama/AI_RSP_Game/blob/main/ShallowAndRandom/RSPGame.py)
- Includes an ["unbeatable" version](https://github.com/Ryuji-Hazama/AI_RSP_Game/blob/main/ShallowAndRandom/RSPGame_unCompetitable.py) where the player can never win.
- There's also ["condensed" version](https://github.com/Ryuji-Hazama/AI_RSP_Game/blob/main/ShallowAndRandom/RSPGame_shorter.py), with the code made as concise as possible for educational purposes.

### -RSP_AIModel

This model was based on code I found online, which I then converted from C to Python.

- [RSP_AIModel.py](https://github.com/Ryuji-Hazama/AI_RSP_Game/blob/main/ShallowAndRandom/RSP_AIModel.py)
- I converted the code from C to Python by myself to understand the basic structure of the shallow learning AI.
- In [_1D version](https://github.com/Ryuji-Hazama/AI_RSP_Game/blob/main/ShallowAndRandom/RSP_AIModel_1D.py), I switched the weight list structure from 1D to 2D to make the AI's behavior easier to understand.

```mermaid
graph TD;
subgraph Y["Learning Process"];
  B{"Was
  prediction
  wrong?"};
  B -->|Yes| C["Update weights"];
  B -->|No| D;
  C --> D[Update History];
end
subgraph Z["Make Prediction"];
  E[/"History"/] --> G["Predict"];
  F[/Pattern weights/] --> G;
end

G --> I[/Prediction/]

A[/Game Results/] --> B;
C -.- H[(Weights)];
H -.-> F;
D --> E;
```

### -RSP_AIModel_wResult_1D

In this version, I added state-based weights (win/draw/lose) to the model, improving its predictions.

- [RSP_AIModel_wResult_1D.py](https://github.com/Ryuji-Hazama/AI_RSP_Game/blob/main/ShallowAndRandom/RSP_AIModel_wResult_1D.py)

```mermaid
graph LR
  A[/History/] --> C["Predict"];
  B[/"State weights +
  Pattern weights"/] --> C;
  C --> D[/Prediction/];
```

### -RSP_AIModel_wResult_2D

This version adds a extra layer of state information, making the AI more aware of the last state.

- [RSP_AIModel_wResult_2D.py](https://github.com/Ryuji-Hazama/AI_RSP_Game/blob/main/ShallowAndRandom/RSP_AIModel_wResult_2D.py)
- That changed the pattern map structure from 1x3 to 3x3 (3 states(win/draw/lose) x 3 outputs (RSP)).
- It is increasing the learning cost.
- However, it is increasing the accuracy of predictions. Such as:
  - The player could throw the same hand every time he/she win.
  - The player could change the hand every time he/she lose.

```mermaid
graph LR;
  A{State} -->|Win| B{{"weights[0]"}} --> E["Predict"];
  A -->|Draw| C{{"weights[1]"}} --> E;
  A -->|Lose| D{{"weights[2]"}} --> E;
  F[/History/] --> E --> G[/Prediction/];
```

### -RSP_AIModel_wResult_2Dex V1 -

Confidence decay, weight normalization and weight limitation were added from this version.

- [RSP_AIModel_wResult_2Dex V1](https://github.com/Ryuji-Hazama/AI_RSP_Game/blob/main/ShallowAndRandom/RSP_AIModel_wResult_2Dex_1_3_0.py)
- Confidence decay is:
  - Calculated from the recent win:draw:lose rate.
  - Using as a weight bias.
    - If the computer keeps winning, it increases confidence.
    - If the computer keeps losing, it decreases confidence and may change the prediction.
- Weight normalization is:
  - If the computer keeps winning, it increases the winning-pattern weights value and decreases the losing-pattern weights value.
  - If the computer keeps losing, it increases the losing-pattern weights value and decreases the winning-pattern weights value.
- Weight limitation is:
  - It limits overgrowth and overdecay (too close to zero) of the weights.
- Those changes make the AI more flexible and adaptable to players' strategy changes.

```mermaid
graph TD;

Bias[/"Win:Draw:Lose
    Bias"/];
We[("Weights")];
ST(["START"]);
His[/"History"/];

  subgraph Lim["Weight Limitation"];
    C{"Are the weights
    inside the limits?"} -->|Too Big|R["Regulate
    the Weights"];
    C -->|Too Small|A["Amplify
    the Weights"];
  end
  subgraph Nor["Weight Normalization"];
    Sv{{"Soft Value"}} --> N["Normalize
    weights"];
  end
  subgraph Pre["Prediction"];
    Dv{{"Decay Value"}} --> P1["Predict"];
    P1 --- iP[/"Prediction"/];
    Pw{{"Pattern Weight"}} --> P1;
  end

  His -.-> P1;
  Bias -.-> Dv;
  Bias -.-> Sv;
  ST ----> Sv;
  We -.-> N;

  N --> C;
  C -->|Yes| Pw;
  R --> Pw;
  A --> Pw;
  Pw -.-> We;
  iP --> E(["END"]);
```

### -RSP_AIModel_wResult_2Dex V2.0

From this version, the weights are initializing with random values to make the model more human-like.

- [RSP_AIModel_wResult_2Dex V2.0](https://github.com/Ryuji-Hazama/AI_RSP_Game/blob/main/ShallowAndRandom/RSP_AIModel_wResult_2Dex_2_0_2.py)
- This gives the model more randomness at the beginning of the game.

### -RSP_AIModel_wResult_2Dex V2.1

This version added the learning decay calculated from win/draw/lose rate.

- [RSP_AIModel_wResult_2Dex V2.1](https://github.com/Ryuji-Hazama/AI_RSP_Game/blob/main/ShallowAndRandom/RSP_AIModel_wResult_2Dex_2_1_2.py)
- If the AI keeps winning and loses once, the AI thinks, "Is this just a random noise? Let it be ignored for now."
- And starts to keep losing, the AI thinks, "Oh, this is true. I need to change strategy now."

```mermaid
graph TD;
  subgraph A["Update Weights"];
    Uv{{"Value for
    Update"}} --> U["Update Weights"];
    Ld{{"Learning Decay"}} --> Uv;
  end
  Bias[/"Win:Draw:Lose
    Bias"/] -.-> Ld;
  H[/History/] -.-> Uv;
  We[("Weights")] <-.-> U;
```

[[Back to Top]](#table-of-contents)

## Whole System Flow Chart

```mermaid
graph TD;

subgraph _MkPre["Make Prediction"]
  mp_StB[\"State Bias"\] --> mp_Make["Make a Prediction"];
  mp_His[\"Pattern History"\] --> mp_Make;
  mp_Make --> mp_SaT["Sort and
  Tag Predictions"];
  mp_SaT --> mp_IniPre{{"Initial Prediction"}};
  mp_IniPre --> mp_AdB["Add bias"];
  mp_Wei[\"Weights"\] --> mp_AdB;
  mp_AdB --> mp_rSaT["Resort and
  Tag Predictions"];
  mp_rSaT --> mp_Pred[/"Prediction"/];
end

subgraph _NormW["Weight Normalization"]
  n_StB[\"State Bias"\] --> n_Norm["Normalize Weight Values"];
  n_oWei[\"Weights"\] --> n_Norm;
  n_Norm --> n_nWei[/"Normalized Weights"/];
end

subgraph _Predict["Prediction"]
  p_FR{"Is this a
  first round?"} ---->|Yes|p_Rnd["Random Prediction"];
  p_FR ---->|No|p_PreRight{"Was prediction
  Right?"};
  p_PlH[\"Player Hand"\] --> p_PreRight;
  p_CmH[\"Predicted Hnad"\] --> p_PreRight;
  p_PreRight -->|Yes| p_UpdateHistory["Update History"];
  p_PreRight -->|No| p_UpdateWeights["Update Weights"];
  p_UpdateWeights --> p_UpdateHistory;
  p_UpdateHistory --> p_Norm[["Normalize the weights"]];
  p_Norm --> p_MkPre[["Make a Prediction"]];
  p_MkPre --> p_Ret[/"Prediction"/];
  p_Rnd --> p_Ret;
end

p_Norm -.- _NormW;
p_MkPre -.- _MkPre;

p_UpdateHistory -.-> His[("History")];
p_UpdateWeights -.- Weight[("Weights")];
His -.- n_StB;
His -.-|State History| mp_StB;
His -.-|Pattern History| mp_His;
Weight -.-> n_oWei;
Weight -.-> mp_Wei;
n_nWei -.-> Weight;

subgraph _Judge["Judge"]
  j_PlH[\"Player Hand"\] --> j_Judge["Judge the Hands"];
  j_CmH[\"Computer Hand"\] --> j_Judge;
  j_Judge --> j_SRes["Show result"];
  j_SRes --> j_Ret[/"Result"/];
end

subgraph _IniVars["Initialize Variables"]
  Vars[\"Variables"\] --> IniVars["Initialize"];
end

Start(["START"]) --> Initial[["Initialize Variables"]] -.- _IniVars;

subgraph MainM["Main"]
  Initial --> W1[/"While True"\];

  subgraph While1["While"]
    W1 --- IniResults{{"Initialize 
    Results"}};
    IniResults --> W2[/"While
      win < 30 and
      lose < 30"\];

    subgraph While2["While"]
      W2 -->|True| Next{nextPredict?};
      Next -->|True|Pred[["Prediction"]];
      Pred --> PrHand{{"Predicted Hand"}};
      Next --> PrHand;
      PrHand --> GetPH["Get Player's
      Hand"];
      GetPH --- m_PlH[\"Player Input"\];
      m_PlH --> ValHand{"Valid Hand"};
      ValHand ---|True|NPTrue{{"nextPredict = True"}};
      ValHand -->|False|Quit1{"Quit?"};
      Quit1 ---|False|NPFalse{{"nextPredict = False"}};
      NPFalse --> WE2[\"Loop"/];
      NPTrue --> Judge[["Judge"]];
      Judge --> UpR["Update Results"];
      UpR --> WE2;
      WE2 --> W2;
    end

    W2 -->|False| ShowR["Show Result"];
    Quit1 -->|True| ShowR;
    ShowR --> Continue{"Continue"};
    Continue -->|"Reset and Continue"|res[["Initialize Variables"]];
    Continue -->|"Continue with
    current memories"|WE1[\"Loop"/];
    res --> WE1;
    WE1 ----> W1;
  end
end

res -.- _IniVars
Judge -.- _Judge;
Pred -.- _Predict;
Continue ---->|False|END(["END"]);

```

---

*What do you feel when you look at the **chart** and the **code** side by side?*

Is this too **chaotic** for a *simple* RSP game? Or is under 1,000 lines of code still too **simple** to reflect our *chaotic* human "thoughts"?

[[Back to Top]](#table-of-contents)
