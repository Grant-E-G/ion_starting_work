# Six-hour sprint work log — 2026-10-14

Active user authorization: six hours of autonomous computational experiments,
starting approximately 11:11 a.m. Pacific, ending approximately 5:11 p.m. Pacific.
Do not stop early, ask C5R for work, buy resources, or alter OmpF. Continue
quantitative experiments and produce final reproducible report at the checkpoint.
The attached folder still contains the incorrect ASIC directive; the latest user
message is the operative membrane-protein directive. Root README/AGENTS read.
No subagents authorized or spawned. GPU works through escalated exec and the
isolated `/tmp/c5r-gpu` environment, as documented in root AGENTS.md.

Current scientific questions:

- Do the released Barethiya 2026 physical features add useful unseen-site or
  unseen-substitution functional selection beyond pretrained sequence models?
- Can EvoEF2 local repacking or pretrained METL physical attributes cheaply
  generate a useful mutation-to-energy mapping for BK gating?
- Does any increment survive stronger actual-mutant sequence representations,
  parameter-efficient adaptation, and rigorous site/publication grouping?
- Does the best approximation transfer to an independent membrane observable?
  ADRB2 signaling data/controls are being audited; no target selected.

Verified findings (interim, not a final decision):

1. Barethiya implementation pinned to SBarethiya/VEP
   bdd02ad997b866cc7585144d14a00a804f092854. Five datasets and all supplied
   Rosetta/RMSF features downloaded with hashes. Released `encode.py` has a
   syntax error in `def enc_llr(...args.mutation_col)` and an AAIndex indexing
   mismatch (20 table rows vs 21-character alphabet). Our executable PyTorch
   port corrects these and reproduces architecture classes, not exact TF1 fits.
   Original nn4dms preprocessing confirms canonical alphabetical AAIndex rows.
2. All new functional partitions frozen before fitting. Mixed-site or
   mixed-substitution combinations are purged. Five seeds 10/24/36/42/56;
   groups 70/15/15. Partition CSVs are ignored; compact expected hashes tracked.
3. BK has 473 unique mutants, 247 sites, 28 censor flags; 445 numeric records
   used for primary new regression. True source-connected grouping has a
   277-variant component. Prior whole-source-string grouping was insufficient.
4. BK published RF reproduced on its original arrays: stored mean r=.703,
   reproduced mean r=.712. Released plotting `rmse()` is MAE, not conventional
   RMSE. Stored MAE ~32 mV, conventional RMSE ~48 mV (squashed target scale).
5. `bk_audit.py` uniquely recovers all original row identities and 30 feature
   columns to <1e-10, verifies train-only StandardScaler and target
   `200*tanh(raw_mV/200)`. Raw table feature energies already correspond to
   published inputs; an initial expanded/extra-tanh feature approximation is
   kept as a diagnostic, not called a faithful feature reproduction. Exact
   energy columns now exposed as `audited_energy` in bk.py.
6. Published BK prospective cases are L235F (56±8), L235H (13±6), V236H
   (-35±7), V236N (-11±7) mV. These are NOT the three pre-existing L235W,
   V236A/W variants. L235A is an additional later censored >150 mV case.
   Same-site means are an essential baseline for those selected examples.
7. EvoEF2 unmodified MIT-licensed source compiled locally. Pab1 1,195
   substitutions took142s/4 workers; GFP 1,817 took369s/3 workers, under shared
   load. BK473 two-state 20-Angstrom patch/subunit-A mutants with matched WT
   repacking took1412s/2 workers. This omits membrane/cofactors and is not a
   gating free energy. WT self-repacking controls reveal appreciable offsets.
8. ESM-2 8M/35M/150M and ESM-1v650M masked features actually generated on GPU.
   Actual mutant35M embeddings are also being computed (large GB1 set195,826
   variants). No new foundation model is trained. GPU LoRA35M tests running.
9. METL source-only physical checkpoints downloaded; never use published
   function-finetuned checkpoints, which would leak test labels. GFP local
   model13,920 constructs55 attributes/256 latent dimensions took23.6s,
   peak197MiB. BK global3D473 mutants/two states took171s, peak802MiB;
   corresponding sequence-only1D model gives exactly zero state differences.
   These are normalized Rosetta-surrogate attributes, not measured free energy.
10. GB1 scores independently verified from original WT sequencing counts:
    ln((sel+.5)/(inp+.5))-ln((WTsel+.5)/(WTinp+.5)), max error4.4e-15 across
    all536,084 rows. Secondary beneficial threshold ln(1.2) now frozen; original
    percentile metrics retained. GFP has a supplied WT-normalized fluorescence
    column; other VEP targets are not yet called WT gains.
11. Nine scientific invariant tests passed initially. Further files need final
    Black/Ruff/mypy/tests after edits. Prior OmpF aggregate hash verification
    passed; no frozen code/data/results changed.

Interim results show correlation gains on some soluble datasets but inconsistent
brighter-than-WT selection. Strict BK prediction is much weaker than random-split
claims. Do not infer a family-level modeling NO-GO. Results and logs are in this
directory; source/raw caches and large generated outputs are intentionally ignored.

Next immediate work: finish/collate active comparisons; wire METL/actual-mutant
features into fair functional comparisons; test original published BK features
under matched preprocessing/splits; inspect ADRB2 author controls and freeze its
new benchmark before fitting; use remaining time for falsifiable experiments,
stronger sequence/physics comparisons, numerical failure analysis and final
reproduction artifacts. The code lives in code/experiments/sprint.

Follow-up audit: the released Barethiya encoder passes mutation-masked integer
sequences to AAIndex; unchanged positions are stop-index0. Original nn4dms
inserts a zero stop row but Barethiya omitted it. Initial port used canonical
full-sequence AAIndex, matching old nn4dms rather than the modified encoding.
All initial results remain diagnostics; new `_maskedAA` runs repair the intended
zero native rows and canonical indices explicitly. S2 settings alone do not make
initial full-encoding cases exact paper reproductions. New controls separate
substitution identities, site means, residual energies and shuffled energies.

ESM-2 3B FP16 actually completed on BK/GFP/Pab1/ADRB2; BK receipt records
6066MiB allocated, 6388MiB reserved, 295.4s for247 sites. Root AGENTS updated.
GB1 single-to-double test: empirical addition beats METL direct readouts and
anchored corrections for improvement over measured parents. This is a strong
baseline requiring extensive measured singles, not a low-data membrane success.
Pure physical readouts are exploratory follow-up; no new training labels used.
ADRB2 frozen core test has only5 replicated response gains /920 and1 joint gain;
structural-core training has zero joint gains. Treat power and WT-control noise
as limitations, not a family-level physics failure. Stronger actual650M and3B
controls continue. BK published matched ablations are complete and show no
reliable strict-holdout energy increment.

At about2h55 into six-hour block (21:06UTC; checkpoint00:11UTC):
- METL source normalization VERIFIED per-PDB mean/std in pinned original training
  code f9bfca5c6853c03adfdd2d699e297cd35693a13e. WT subtraction removes
  mean, NOT unknown std. State contrasts remain normalized descriptors, never
  calibrated energy differences. Independent closed/open concatenation test
  running in bk_metl_two_state.log. Do not call nonzero normalizedref state
  differences physical-invariance failures without unscaling.
- Full BK scan CSVs downloaded20x856, ALL473original30inputs exactlymatch.
  WT energy/hydropathy deltas exactlyzero. bk_nullaware.py tests fixedRF,
  WTanchoring/augmentation. Anchoring helps some positive-shift rankings but
  physics increment still inconsistent; pooledOOFprecision can reverse meanfold
  ordering, so report primary meanfold metrics and label pooled CI separately.
- Capped-development-label experiments: GFP64train+32val=96total, METL physical
  vs random; paired tabular35/650actual embeddings, energies/METL; ESM35frozen
  heads andLoRA3featuremodes. Fullvalidation64train runs are NOT64label workflows.
  GB1METLbinding vsstandard with1000train+256val and fullval continue.
- Energy crop sensitivity24label-blind mutants:20vs28A scorestate rho=.9974,
  RMSchange .0084 vsreferenceRMS14.95, signagreement1. Engine has6A cutoffs,
  so this only validates crop adequacy for that finite-rangeengine, not physics.
  12Aoneinput E399R crashes;23pairedrho.75 and70%signagreement. No engine debugging.
- BK conditions audit: all473uniquelyjoin workbook data_complete.13labels match
  Hoshi2013 hSlo1+beta1 Table1, not alpha-alone.30nominalnonzeroCa, only2>10nM
  (D434G100nM,N806K2uM).339mouse/133human/1rat; template human.45numericlabels
  within10mV of50threshold. No label corrected. Context-aware and human-only
  diagnostic fits in condition_compare.log. Unknown auxiliary context staysunknown.
- Independent2024 Table1 PMC11309983 curated:12zeroCa point genotypes,2overlap
  controls L312A/M304A,10new.4new left-shift gains ALLshareL312A;3retain>=80%
  WT apparent slope. Need known-parent baseline and increments relative matched
  L312A. No novel combo improves parent by>=10mV; cannot prove engineering gains.
  Other10/25uM rows NEVERgradedzeroCa. ActualGenBankAAB65837 retrieved1113aa,
  first1056identicalto1065aaPDBreference; allpore1022windows identical, Ctailunmodeled.
  Externaldata/sequence/energy code nowrunning; external_bk_compare.py fits/tunes
  on old445only and tests10novelgenotypes. Actual650mutant-minusWTfeatures
  generated473old+15external,15nativewindows,67s,peak2773MiB; cachecheck7.6e-6.
- GPUprecisionprobe650M length1022batch2: FP32median3.46s vsautocast1.83s,
  pairedsharedload1.895x speedup; actualmutation-delta relativeL2errors0.54/0.81%,
  passes predeclared5%tolerance. ExternalfeaturesremainFP32; no functional
  accuracy guarantee. See gpu_precision_probe.json.
- Evo externalcompound105char path crashed upstream100char Cbuffer. Relative
  path experiment fixed immediately. energy.score now stages identicalbytes
  under short local tempfile name; no scientific engine edit. New longpath
  invariant test added. Old retained models maxpath88 (<100), so unaffected.
  Same-unioncrop/repacking controls prevent spurious physicalepistasis; all
  externaljoint computations nowfinished. I233-L312 closestheavy distance>21A,
  so do not waste a C4repeat expecting direct6A interactions. Missing standalone
  functions means externalconditionalchanges are NOT experimentalepistasis.
- BoostedPCA32nonlinearclassifier tests whether sequence highdimension/linear
  readout hides physics; fixedAPvalidation, no newsimulator, stillrunning.
- Barethiya port correction2: paper uses RAWLLR; genericport /10 keptdiagnostic.
  New `_S2_maskedAA_rawLLR` uses properrawscale. OldmaskedS2esm cases /10 are
  diagnostic. NewmaskedAA generic5seedcontrols nearlyfinished; source12site
  identitymean/residualenergy controls also running/finished. ExactTFnumbers
  neverclaimed: newpartitions/trainingbudgets and repairedcode.
- Last tests13passed andmypy30filespassed BEFOREnewexternal/condition scripts
  andlongpath test. Need finalBlackindividualfiles/Ruff/mypy/pytest. cache.py
  verifies379resources before externalmanifest; addexternal_bk_sources.json
  andfinalsource manifests, pinNN4dmsURLs now434e354828f306cbb6796033ef1169cbe5207350.
- Current major jobs logs: ve pmasked+S2raw, METLGB1full/val256, GFP64full/96total,
  finetune_gfp96total, tabular_gb1_val256, ADRB2actual650(5600/7799), boosted,
  condition_compare, bk_metl_two_state. No new GPUjobs needed untilthese finish.
  ADRB2actual650oldworker writes adrb2_esm1v_650m.npz; AFTERfinish rename to
  *_mutant_embeddings.npz (code fixed namespace).35actual alreadyrenamed;3B
  masked file stays originalname. Then run stronger650/3B+physics comparisons
  withnewtags; existingADRB2metrics lacked3B/650 when captured.
- Stillmust build final reporting/uncertainty/failure analyses, curated reproducible
  result artifacts andrequirements/README. OmpF untouched, freezecheckpassed.
  Do notfinish early; ~3hremain. No subagents, purchases, C5Rrequests or targetcommit.

## 21:49UTC checkpoint (~2h22 remain before00:11UTC)

- ENCoM published NRGten1.2.9/pyvcon1.0.2 installed no-deps into CPU stack,
  source archives hashed. Native273-residue TMD monomer numerical checks pass:
  repeated entropy error0, rotated/translatedPDB entropy difference0.000347,
  six rigid modes, positive remaining spectrum, Hessian symmetry7.3e-12,
  rigid-translation residual2.4e-16. Full274genotype matched-self feature run
  at220/274, ~25minelapsed. **After completion run encom_compare.py and
  external_bk_compare.py --encom**, both not yet launched. Same TM cohort for
  all baselines; pseudo-physicalentropy/work not gatingfreeenergies.
- Independent BK2024 all comparisons completed. Known-parent-only MAE16mV,
  sequence34.6mV, sequence+Evo35.4mV. No model beats no-change-fromL312A for
  four added-substitution effects. Allfour leftgains inheritknownL312A. Exact
  source accession sequence, controls, state-specific patches and parent
  contrasts saved. GPU650actualdelta features67s; autocastpairedprobe1.895x
  speedup with<1%delta-vectorerror, documented in rootAGENTS.
- ADRB2strongregression done; strongclassification done/nearlydone. Sequence650
  and3B features nowavailable. Jointgain constraintP20remains0 for models in
  currentregression, but coretestonly1jointpositive; nofamily-levelNO-GO.
- Hydration fullprofiles had numericalRidgeextrapolation to millionsmV from
  nearconstanttraining columns. Added bounded --stable train-onlyvariance1e-10
  filter, preservedold outputs. SiteRidgeRMSE~260mV afterstabilization versus
  WT-null~85mV, no useful increment fromhydrationgrid beyondfullinputprofiles.
  Treatthis asapproximation/cohortfailure, notwaterphysicsrejection.
- Newly started independent Wu2016GB1 transfer: primaryauthorsrepo
  dbdd7639187e0b8f22359f404ce4d1d950fcc8a9,149361measured canonicalvariants.
  Source Mutfit I20fit **overwrites singles witholdOlsonlabels**; useverified
  I20fitRaw fromactualinput/IGG20WTcounts, excludeallimputeddata. Test147193
  (?) measured3/4mutants, fourmutatedsites completelyexcludedfromallold
  supervisedtraining+validation. Newgb1_transfer.py prepare/features/compare;
  featuresrunningGPU: METLbinding14936156.3s186MiB,matchedSTANDARD52.2s,
  ESM35actual149361stillrunning. Afterfinished runcompare CPU. Scriptwas
  modifiedwhileworkeractive toaddoptionalnative_pooledwriter; workeroutputs
  omitthatkeybutcompareusesexistinggb1_esm2_35m.npz wt_hiddenmeanso fine.
  Sourcepolicy frozen; noWu label usedforfitting,old1000+256labels only.
  Empiricalallconstituent singles/pairs strongcontrols usemoreexistinglabels,
  eligibilitymasksandlabelbudgetexplicit. Poissonreadcountsupportsecondary
  notbiologicalreplicate/significanceclaim. Needcheckfinalnumbersandunits.
- collect.py nowcorrectsVEPGB1metrics toverifiedWTln1.2 fromfixedpredictions,
  otherunverifiedPab/Ube/Bglmetricsclearlytopdecileonly. selection_audit.py
  fixedpairedmethodcontrasts (notbest-testselection),86pairs snapshot. Rerun
  collectandselectionafterremainingjobsfinish. neural_cases snapshotstillold.
- CPU/GPU requirementlockfiles writtenusingUV_CACHE_DIR=/tmp/c5r-uv-cache.
  sprintREADME describesmethodports,caveats,commanddependencies,sourcepins.
  manifest.py wrote9datasetmeasurement/structuremanifest,147outputhashes;
  rerunatendwhenmoreoutputsfinish. cache.py verify383scientificinputs passed
  beforeadding5Wu2016files; rerunfinal.14scientifictests passed; fifteenth
  addedWu rawfitness+heldoutsitechecks notrunyet. Ruff/mypy44filespassed
  before2newfiles; rerunBlack(file-by-file),Ruff,mypy,pytest atfinal.
- Mainremainingjobs: GB1METLfullvalidation(atmutation24control), capped256
  (mutation42control), GFP96ESMfinetune(lastmutation56LoRArosetta),
  BKmetl_two_state(publicationfold0of5),ENCoMfeatures,GB1transferfeatures.
  Plentytimeforfinalcomparisonsandreport. **No finaldecision_report.md yet**;
  mustwritewithactualfinishedresults,rankedmethods,nextcomputationalexperiment,
  sourcecitations,limitations. RootREADMEneedslink. NoOmpFchanges/noC5Rrequests.

## Founder stop / cleanup handoff

The sprint hit the token usage limit. The founder requested cleanup and an external-agent review. All experiment workers have exited; no new experiments were started during cleanup. Seventeen scientific tests, Ruff and mypy(56files) pass.389scientific resources verify and allOmpFfreezehashes match. SixrandomKirfeaturecaches are generated but readout comparisons remainUNRUN. Reviewbrief, decisionreport, quantitativeappendix and reviewarchive are the handoff; no prospectiveengineeringclaim or targetcommitment.
