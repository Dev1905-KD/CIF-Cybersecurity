import re


class ConsistencyAgent:

    def verify(
        self,
        answer,
        context
    ):

        findings = []

        answer_cves = self._extract_cves(
            answer
        )

        context_cves = self._extract_cves(
            context
        )

        # ---------------------------------
        # 1. CVE consistency
        # ---------------------------------

        for cve in answer_cves:

            if cve not in context_cves:

                findings.append({
                    "type": "CVE_MISMATCH",
                    "severity": "High",
                    "message":
                        f"{cve} appears in the answer "
                        "but not in the retrieved context."
                })

        # ---------------------------------
        # 2. Product consistency
        # ---------------------------------

        context_products = (
            self._extract_products(context)
        )

        answer_products = (
            self._extract_products_from_answer(
                answer,
                context_products
            )
        )

        for product in answer_products:

            if not self._product_matches(
                product,
                context_products
            ):

                findings.append({
                    "type": "ENTITY_MISMATCH",
                    "severity": "Medium",
                    "message":
                        f"Product/entity '{product}' "
                        "appears in the answer but "
                        "was not found in the retrieved context."
                })

        # ---------------------------------
        # 3. Source consistency
        # ---------------------------------

        context_sources = (
            self._extract_sources(context)
        )

        answer_sources = (
            self._extract_sources(answer)
        )

        for source in answer_sources:

            if source not in context_sources:

                findings.append({
                    "type": "SOURCE_MISMATCH",
                    "severity": "Medium",
                    "message":
                        f"Source '{source}' is mentioned "
                        "in the answer but was not found "
                        "in the retrieved context."
                })

        # ---------------------------------
        # 4. Contradiction checks
        # ---------------------------------

        contradiction_patterns = [
            (
                r"not affected",
                r"affect"
            ),
            (
                r"does not affect",
                r"affect"
            ),
            (
                r"not vulnerable",
                r"vulnerab"
            ),
            (
                r"no evidence",
                r"evidence:"
            )
        ]

        answer_lower = answer.lower()
        context_lower = context.lower()

        for negative_pattern, positive_pattern in (
            contradiction_patterns
        ):

            if re.search(
                negative_pattern,
                answer_lower
            ) and re.search(
                positive_pattern,
                context_lower
            ):

                findings.append({
                    "type": "POTENTIAL_CONTRADICTION",
                    "severity": "High",
                    "message":
                        "The answer may contradict "
                        "information in the retrieved context."
                })

        # ---------------------------------
        # 5. Overall status
        # ---------------------------------

        high_count = sum(
            1
            for finding in findings
            if finding["severity"] == "High"
        )

        medium_count = sum(
            1
            for finding in findings
            if finding["severity"] == "Medium"
        )

        if high_count > 0:

            status = "Inconsistent"

        elif medium_count > 0:

            status = "Needs Review"

        else:

            status = "Consistent"

        return {
            "agent": "Consistency Agent",
            "status": status,
            "findings": findings,
            "checks": {
                "cve_consistency": (
                    len(answer_cves) > 0
                    and all(
                        cve in context_cves
                        for cve in answer_cves
                    )
                ),
                "entity_consistency": (
                    len(answer_products) == 0
                    or all(
                        self._product_matches(
                            product,
                            context_products
                        )
                        for product in answer_products
                    )
                ),
                "source_consistency": (
                    len(answer_sources) == 0
                    or all(
                        source in context_sources
                        for source in answer_sources
                    )
                )
            }
        }

    # ---------------------------------
    # CVE extraction
    # ---------------------------------

    def _extract_cves(self, text):

        return set(
            re.findall(
                r"CVE-\d{4}-\d{4,7}",
                text.upper()
            )
        )

    # ---------------------------------
    # Product extraction from context
    # ---------------------------------

    def _extract_products(self, context):

        products = []

        in_product_section = False

        for line in context.splitlines():

            line = line.strip()

            if line.lower() == "affected products:":

                in_product_section = True

                continue

            if (
                in_product_section
                and line.startswith("- ")
            ):

                product = line[2:].strip()

                if product:
                    products.append(product)

            elif (
                in_product_section
                and line
                and not line.startswith("- ")
            ):

                in_product_section = False

        return products

    # ---------------------------------
    # Product/entity extraction
    # ---------------------------------

    def _extract_products_from_answer(
        self,
        answer,
        context_products
    ):

        products = []

        # ---------------------------------
        # 1. Explicit product declarations
        # ---------------------------------

        patterns = [
            r"affected products?\s*[:\-]\s*([^\n.]+)",
            r"vulnerable products?\s*[:\-]\s*([^\n.]+)",
            r"products?\s+affected\s*[:\-]\s*([^\n.]+)"
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                answer,
                flags=re.IGNORECASE
            )

            for match in matches:

                value = match.strip()

                if value:
                    products.append(value)

        # ---------------------------------
        # 2. Match known graph/context
        #    products directly in answer
        # ---------------------------------

        answer_lower = answer.lower()

        for context_product in context_products:

            product = context_product.strip()

            if not product:
                continue

            if product.lower() in answer_lower:

                products.append(product)

        return list(
            dict.fromkeys(products)
        )

    # ---------------------------------
    # Product matching
    # ---------------------------------

    def _product_matches(
        self,
        answer_product,
        context_products
    ):

        answer_words = set(
            self._normalize_words(
                answer_product
            )
        )

        if not answer_words:
            return False

        for context_product in context_products:

            context_words = set(
                self._normalize_words(
                    context_product
                )
            )

            if not context_words:
                continue

            overlap = (
                answer_words & context_words
            )

            ratio = (
                len(overlap)
                / len(answer_words)
            )

            if ratio >= 0.60:
                return True

        return False

    # ---------------------------------
    # Source extraction
    # ---------------------------------

    def _extract_sources(self, text):

        sources = set()

        source_names = [
            "NVD",
            "CISA KEV",
            "MITRE ATT&CK",
            "MITRE"
        ]

        text_upper = text.upper()

        for source in source_names:

            if source.upper() in text_upper:

                sources.add(source)

        return sources

    # ---------------------------------
    # Text normalization
    # ---------------------------------

    def _normalize_words(self, text):

        return re.findall(
            r"\b[a-z0-9]+\b",
            text.lower()
        )