#!/usr/bin/env bash
# Stage 1 on the new source: index full_705k_v2_filtered once, then run the FROZEN v1 queries
# (production + diagnostic) unchanged, with the GUIDANCE FWI disambiguation rule, and report
# overlaps. Restartable: the indexer skips finished buckets; finished query runs are skipped.
# Run inside screen on a Polaris login node, in a Python env with duckdb importable.
set -euo pipefail
export LC_ALL=C
BASE="${LITCOLLECT_ROOT_POLARIS:?set to config/local_paths.yaml:litcollect_root_polaris}"
SRC=$BASE/sources/full_705k_v2_filtered
IDX=$BASE/index/full_705k_v2_filtered
RUNS=$BASE/runs/705k
LOG=$BASE/reports/705k_stage1.log
mkdir -p "$RUNS" "$BASE/reports" "$BASE/ids"
exec > >(tee -a "$LOG") 2>&1
echo "=== START $(date -u +%FT%TZ) host=$(hostname) python=$(python -c 'import sys;print(sys.version.split()[0])') duckdb=$(python -c 'import duckdb;print(duckdb.__version__)')"

echo "=== STEP A: build index"
python "$BASE/scripts/build_index.py" --root "$SRC" --out "$IDX"

echo "=== STEP B: frozen v1 queries"
for q in fire_weather_v1 extreme_heat_v1 fire_weather_diag_topical_only extreme_heat_diag_topical_only; do
  if [ -s "$RUNS/$q/summary.json" ]; then echo "skip $q (done)"; continue; fi
  args=(--index "$IDX" --query-file "$BASE/queries/${q}_query.txt" --out "$RUNS/$q" --name "${q}_705k")
  case "$q" in fire_weather*) args+=(--disambiguate 'fwi=fire weather|fire-weather');; esac
  python "$BASE/scripts/run_query.py" "${args[@]}"
done

echo "=== STEP C: overlaps"
sort "$BASE/sources/previous_corpus_ids.txt" > "$BASE/ids/previous_corpus_ids_sorted.txt"
cut -d, -f4 "$IDX/manifest.csv" | tail -n +2 | sort > "$BASE/ids/full_705k_ids.txt"
echo "legacy 1918 ids present in 705k source: $(comm -12 "$BASE/ids/full_705k_ids.txt" "$BASE/ids/previous_corpus_ids_sorted.txt" | wc -l)"
for q in fire_weather_v1 extreme_heat_v1 fire_weather_diag_topical_only extreme_heat_diag_topical_only; do
  echo "$q: admitted=$(wc -l < "$RUNS/$q/ids.txt") raw=$(wc -l < "$RUNS/$q/ids_raw.txt") overlap_with_legacy_1918=$(comm -12 "$RUNS/$q/ids.txt" "$BASE/ids/previous_corpus_ids_sorted.txt" | wc -l)"
done
echo "fire_weather_v1 ∩ extreme_heat_v1: $(comm -12 "$RUNS/fire_weather_v1/ids.txt" "$RUNS/extreme_heat_v1/ids.txt" | wc -l)"
echo "fire_weather_v1 ⊂ diag: $(comm -12 "$RUNS/fire_weather_v1/ids.txt" "$RUNS/fire_weather_diag_topical_only/ids.txt" | wc -l)"
echo "extreme_heat_v1 ⊂ diag: $(comm -12 "$RUNS/extreme_heat_v1/ids.txt" "$RUNS/extreme_heat_diag_topical_only/ids.txt" | wc -l)"
for a in fire_weather_v1 extreme_heat_v1 fire_weather_diag_topical_only extreme_heat_diag_topical_only; do
  echo "--- $a"; python -c "import json,sys;s=json.load(open(sys.argv[1]));print({k:s[k] for k in ('documents_in_index','per_group_doc_counts','raw_count','admitted_count','excluded_by_disambiguation','elapsed_seconds')})" "$RUNS/$a/summary.json"
done
# Hash everything that will be cited.
( cd "$BASE" && sha256sum queries/*.txt index/full_705k_v2_filtered/manifest.csv index/full_705k_v2_filtered/index_summary.json runs/705k/*/summary.json runs/705k/*/ids.txt runs/705k/*/hits.csv ) > "$BASE/reports/705k_stage1_hashes.txt"
echo "=== ALL_DONE $(date -u +%FT%TZ)"
