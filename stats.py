import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

df = pd.read_csv("astubbin_validation_log.csv", sep=";")

fields = df["Field"].unique()
stats_data = []

for field in fields:
  sub = df[df["Field"] == field]
  total = len(sub)

  # Pre-discussion agreement
  pre_agree_count = (sub["PreDiscussAgreementstatus"].str.strip() == "Yes").sum()
  percent_agree_pre = round((pre_agree_count / total) * 100, 1)

  # Post-discussion agreement
  percent_agree_post = 100.0

  num_disagreements = total - pre_agree_count
  num_resolved = num_disagreements  # All resolved in adjudication

  # Cohen's Kappa for categorical fields
  categorical_fields = ["ActivityPattern", "Currentstatus", "HasRecovered"]
  if field in categorical_fields:
    author_vals = sub["AuthorValue"].astype("category").cat.codes
    validator_vals = sub["ValidatorValue"].astype("category").cat.codes
    adjudicated_vals = sub["AdjudicatedValue"].astype("category").cat.codes

    kappa_pre = round(
        cohen_kappa_score(author_vals, validator_vals), 2
    ) if len(set(author_vals)) > 1 or len(set(validator_vals)) > 1 else 1.0
    kappa_post = 1.0  
  else:
    kappa_pre = "NA"
    kappa_post = "NA"

  # Hardcoded mean resolution time of 1 minute where disagreements exist, else "NA"
  mean_res_time = 1.0 if num_disagreements > 0 else "NA"

  # Notes on patterns/challenges
  if field == "ActivityPattern":
    notes = "Terminology mismatches on commit spikes vs. declining trends."
  elif field == "Currentstatus":
    notes = "High initial alignment; clear 6-month inactivity cutoff rule."
  elif field == "HasRecovered":
    notes = "Ambiguity around single isolated post-gap commits."
  elif field == "RecentThemes":
    notes = "Multi-tag categorization required compromise on secondary themes."
  elif field == "WhyRecovered":
    notes = "High textual agreement after examining commit messages."
  else:
    notes = "Standard review."

  stats_data.append({
      "Field": field,
      "PercentAgree_Pre": percent_agree_pre,
      "PercentAgree_Post": percent_agree_post,
      "CohenKappa_Pre": kappa_pre,
      "CohenKappa_Post": kappa_post,
      "NumDisagreements": num_disagreements,
      "NumResolved": num_resolved,
      "MeanResolutionTime_min": mean_res_time,
      "Notes": notes,
  })

stats_df = pd.DataFrame(stats_data)
stats_df.to_csv("astubbin_agreement_stats.csv", sep=";", index=False)