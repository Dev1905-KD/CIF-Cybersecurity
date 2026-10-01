from rag.crag_llama_pipeline import CRAGLlamaPipeline


def print_line(char="=", length=70):
    print(char * length)


def print_section(title):
    print()
    print_line()
    print(f"  {title}")
    print_line()


def main():

    print_line()
    print("          CIF - CYBERSECURITY INTELLIGENCE")
    print_line()

    print("\nCognitive Intelligence Framework for Cybersecurity")
    print("Evidence-Aware Threat Analysis and Verification\n")

    print("Enter a cybersecurity query.")
    print("Example: CVE-2026-0257")
    print("Type 'exit' to quit.\n")

    pipeline = CRAGLlamaPipeline()

    try:

        while True:

            query = input("CIF > ").strip()

            if query.lower() == "exit":
                print("\nExiting CIF.")
                break

            if not query:
                print("\nPlease enter a query.")
                continue

            print()
            print_line("-")

            print("[1] Processing query...")
            print("[2] Retrieving cybersecurity evidence...")
            print("[3] Checking retrieval quality...")
            print("[4] Building evidence context...")
            print("[5] Generating Llama assessment...")
            print("[6] Verifying generated claims...")
            print("[7] Running multi-agent verification...")

            print_line("-")

            try:

                result = pipeline.run(query)

            except Exception as e:

                print("\nCIF PIPELINE ERROR")
                print_line("-")
                print(str(e))
                print_line("-")
                print(
                    "\nCheck that Neo4j, Ollama, and the required "
                    "Python components are running."
                )

                continue

            # =========================================================
            # ERROR / INSUFFICIENT EVIDENCE
            # =========================================================

            if result.get("status") == "insufficient_evidence":

                print_section("CIF SECURITY ASSESSMENT")

                print(f"Query:")
                print(f"  {query}")

                print("\nRetrieval Status:")
                print(
                    f"  {result.get('evidence_status', 'Unknown')}"
                )

                print("\nFinal Verification Status:")
                print("  INSUFFICIENT EVIDENCE")

                print("\nMessage:")
                print(
                    f"  {result.get('message', 'No sufficient evidence found.')}"
                )

                print_section("RECOMMENDATION")

                print(
                    "  CIF could not establish a sufficiently "
                    "supported assessment."
                )

                print(
                    "  Additional cybersecurity evidence is required."
                )

                print()
                continue

            # =========================================================
            # NORMAL SUCCESSFUL RESULT
            # =========================================================

            if result.get("status") != "success":

                print_section("CIF ERROR")

                print(result)

                print()
                continue

            retrieval = result.get(
                "retrieval",
                {}
            )

            grading = retrieval.get(
                "grading",
                {}
            )

            multi_agent = result.get(
                "multi_agent_verification",
                {}
            )

            evidence_agent = multi_agent.get(
                "evidence_agent",
                {}
            )

            graph_agent = multi_agent.get(
                "graph_agent",
                {}
            )

            consistency_agent = multi_agent.get(
                "consistency_agent",
                {}
            )

            consensus = multi_agent.get(
                "consensus",
                {}
            )

            # =========================================================
            # MAIN ASSESSMENT
            # =========================================================

            print_section("CIF SECURITY ASSESSMENT")

            print(f"Query:")
            print(f"  {query}")

            print("\nRetrieval Status:")
            print(
                f"  {result.get('evidence_status', 'Unknown')}"
            )

            print("\nFinal Verification Status:")
            print(
                f"  {consensus.get('status', 'Unknown')}"
            )

            # =========================================================
            # RETRIEVAL INFORMATION
            # =========================================================

            print_section("EVIDENCE RETRIEVAL")

            print(
                f"Retrieval Quality:"
            )

            print(
                f"  {grading.get('status', 'Unknown')}"
            )

            print(
                "\nSources used by CIF:"
            )

            context = retrieval.get(
                "context",
                ""
            )

            # Try to identify common sources in retrieved context.
            sources_found = []

            for source in [
                "NVD",
                "CISA KEV",
                "MITRE ATT&CK",
                "CSTI"
            ]:

                if source.lower() in context.lower():

                    sources_found.append(source)

            if sources_found:

                for source in sources_found:
                    print(f"  ✓ {source}")

            else:

                print("  ✓ Retrieved cybersecurity evidence")

            # =========================================================
            # LLAMA ASSESSMENT
            # =========================================================

            print_section("LLAMA THREAT ASSESSMENT")

            answer = result.get(
                "answer",
                "No assessment generated."
            )

            print(answer)

            # =========================================================
            # CLAIM VERIFICATION
            # =========================================================

            print_section("CLAIM VERIFICATION")

            claim_verification = result.get(
                "claim_verification",
                {}
            )

            if isinstance(
                claim_verification,
                dict
            ):

                print(
                    f"Status: "
                    f"{claim_verification.get('status', 'Unknown')}"
                )

                if "total_claims" in claim_verification:

                    print(
                        f"Total Claims: "
                        f"{claim_verification.get('total_claims')}"
                    )

                if "supported" in claim_verification:

                    print(
                        f"Supported: "
                        f"{claim_verification.get('supported')}"
                    )

                if "partially_supported" in claim_verification:

                    print(
                        f"Partially Supported: "
                        f"{claim_verification.get('partially_supported')}"
                    )

                if "unsupported" in claim_verification:

                    print(
                        f"Unsupported: "
                        f"{claim_verification.get('unsupported')}"
                    )

            else:

                print(claim_verification)

            # =========================================================
            # MULTI-AGENT VERIFICATION
            # =========================================================

            print_section("MULTI-AGENT VERIFICATION")

            # -------------------------
            # Evidence Agent
            # -------------------------

            print("Evidence Agent")
            print(
                f"  Status: "
                f"{evidence_agent.get('status', 'Unknown')}"
            )

            if "total_claims" in evidence_agent:

                print(
                    f"  Claims checked: "
                    f"{evidence_agent.get('total_claims')}"
                )

            if "supported" in evidence_agent:

                print(
                    f"  Supported: "
                    f"{evidence_agent.get('supported')}"
                )

            if "partially_supported" in evidence_agent:

                print(
                    f"  Partially supported: "
                    f"{evidence_agent.get('partially_supported')}"
                )

            if "unsupported" in evidence_agent:

                print(
                    f"  Unsupported: "
                    f"{evidence_agent.get('unsupported')}"
                )

            print()

            # -------------------------
            # Graph Agent
            # -------------------------

            print("Graph Agent")

            print(
                f"  Status: "
                f"{graph_agent.get('status', 'Unknown')}"
            )

            print(
                f"  Entities checked: "
                f"{graph_agent.get('entities_checked', 0)}"
            )

            print(
                f"  Entities found: "
                f"{graph_agent.get('entities_found', 0)}"
            )

            print()

            # -------------------------
            # Consistency Agent
            # -------------------------

            print("Consistency Agent")

            print(
                f"  Status: "
                f"{consistency_agent.get('status', 'Unknown')}"
            )

            checks = consistency_agent.get(
                "checks",
                {}
            )

            if checks:

                print(
                    f"  CVE consistency: "
                    f"{checks.get('cve_consistency', 'Unknown')}"
                )

                print(
                    f"  Entity consistency: "
                    f"{checks.get('entity_consistency', 'Unknown')}"
                )

                print(
                    f"  Source consistency: "
                    f"{checks.get('source_consistency', 'Unknown')}"
                )

            # =========================================================
            # CONSENSUS
            # =========================================================

            print_section("FINAL CONSENSUS")

            print(
                f"Overall Status:"
            )

            print(
                f"  {consensus.get('status', 'Unknown')}"
            )

            verification = consensus.get(
                "verification",
                {}
            )

            if verification:

                print("\nAgent Results:")

                print(
                    f"  Evidence Agent     : "
                    f"{verification.get('evidence', 'Unknown')}"
                )

                print(
                    f"  Graph Agent        : "
                    f"{verification.get('graph', 'Unknown')}"
                )

                print(
                    f"  Consistency Agent  : "
                    f"{verification.get('consistency', 'Unknown')}"
                )

            # =========================================================
            # FACULTY-FRIENDLY INTERPRETATION
            # =========================================================

            print_section("CIF INTERPRETATION")

            final_status = consensus.get(
                "status",
                "Unknown"
            )

            retrieval_status = result.get(
                "evidence_status",
                "Unknown"
            )

            print(
                f"  Retrieval: "
                f"{retrieval_status}"
            )

            print(
                f"  Verification: "
                f"{final_status}"
            )

            if final_status == "Supported":

                print(
                    "\n  CIF has retrieved relevant evidence "
                    "and the verification agents support "
                    "the generated assessment."
                )

            elif final_status == "Needs Review":

                print(
                    "\n  CIF retrieved relevant evidence, "
                    "but at least one verification component "
                    "requires further review."
                )

                print(
                    "  The system therefore does not blindly "
                    "accept the Llama-generated assessment."
                )

            else:

                print(
                    "\n  CIF recommends additional evidence "
                    "or human review before accepting the assessment."
                )

            # =========================================================
            # END OF RESULT
            # =========================================================

            print()
            print_line()

            print(
                "Enter another query or type 'exit' to quit."
            )

            print()

    finally:

        try:
            pipeline.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()