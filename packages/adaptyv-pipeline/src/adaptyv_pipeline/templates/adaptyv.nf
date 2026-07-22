// Nextflow module: the Adaptyv wet lab as a pipeline process.
// The chain of reproducibility now extends past the lab door.
//
// Usage in a workflow:
//   include { ADAPTYV_ASSAY } from './adaptyv.nf'
//   ADAPTYV_ASSAY(ch_designs_fasta)

nextflow.enable.dsl=2

process ADAPTYV_ASSAY {
    tag "adaptyv-${task.index}"
    publishDir "results/adaptyv", mode: 'copy'

    input:
    path designs_fasta

    output:
    path "run.state.json", emit: state
    path "*.zip",          emit: package, optional: true

    script:
    def execute = params.adaptyv_execute ? '--execute' : ''
    def budget  = params.adaptyv_budget  ?: 0
    """
    # Dry-run by default: no submission, no spend, unless --execute is passed.
    adaptyv-pipeline run ${designs_fasta} \\
        --assay ${params.adaptyv_assay ?: 'affinity'} \\
        --budget ${budget} ${execute} \\
        --model-version "${params.model_version ?: 'unknown'}" \\
        --tracker tracker.jsonl \\
        --state-dir .
    cp .adaptyv-runs/*.state.json run.state.json 2>/dev/null || cp *.state.json run.state.json
    """
}
