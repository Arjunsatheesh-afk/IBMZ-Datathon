# Demo video script (3:00 maximum)

Narrator: Arjun. Screen/terminal: Linux person (server) and dashboard person (app).
Rule: say only what we measured. Numbers were measured on the server; re-check them before recording.

## 0:00-0:20  The problem (face or title slide)
"Banks need fraud models, but the people and tools that touch the data should never see
real identities. Our project, The STARK Paradox, detects fraud on tokenized, encrypted
transactions. The model never sees a raw customer ID."

## 0:20-0:50  The design (architecture.drawio exported as a picture)
"Customer IDs are replaced with HMAC-SHA256 tokens, so the same customer always gets the
same token. The originals are stored AES-GCM encrypted in a separate vault. Only a
Reviewer, with a name and a written reason, can decrypt, and every decryption is logged."

## 0:50-1:20  The data and the honesty (notebook or README table)
"We used PaySim: 6.3 million synthetic transactions, 8,213 of them fraud. Fraud only
occurs in TRANSFER and CASH_OUT, so we model those. Kaggle warns that the balance columns
leak the answer, so we deliberately did not use them.
We proved tokenization costs no accuracy: features computed from raw IDs and from tokens
are identical. ROC-AUC is 0.93. If analysts review the top 600 alerts, 97% are real fraud."

## 1:20-1:55  Running on IBM LinuxONE (terminal: uname -m, docker ps)
"This runs on an IBM LinuxONE server: s390x, in a container. The scoring function takes
about 4 milliseconds per transaction; through the API it is 4.2 milliseconds median and
5.7 at the 95th percentile. We also completed both IBM labs on this platform."

## 1:55-2:40  The dashboard (live demo)
"Analyst view: tokens only, sorted by risk, with the reason for each alert. Reviewer view:
pick a token, enter a name and a reason, and re-identify. Here is the original ID, and
here it is in the audit log."

## 2:40-3:00  Limits and close
"Limits: PaySim is synthetic, risk scores are for ranking, not calibrated
probabilities, the time-of-day signal is partly a simulation effect, and
the role selector is a demo, not production authentication. Next: real authentication and
a tamper-evident audit log. Privacy and fraud detection do not have to be a trade-off.
Thank you."

## Do NOT say
- "Verified NNPA acceleration" (we only know the plugin is installed and loaded).
- "99.8% accuracy" (training batches were balanced 50/50).
- "Production-ready security" (the role selector is a demo).
