class CustomerAgent:

    def __init__(self, context):
        self.context = context

    # ==========================================================
    # INTERNAL ANALYSIS FUNCTIONS
    # ==========================================================


    def _generate_customer_personas(
            self,
            research
    ):
        """
        Generates customer personas from research data.
        """

        personas = []

        audience = research.get(
            "target_audience",
            []
        )

        for customer in audience:

            personas.append({

                "name":
                    customer.get(
                        "segment",
                        "General User"
                    ),

                "age_group":
                    customer.get(
                        "age_group",
                        "Unknown"
                    ),

                "occupation":
                    customer.get(
                        "occupation",
                        "Unknown"
                    ),

                "goals":
                    customer.get(
                        "goals",
                        []
                    ),

                "pain_points":
                    customer.get(
                        "pain_points",
                        []
                    )

            })

        return personas



    def _identify_customer_pain_points(
            self,
            research
    ):

        """
        Extracts unique customer problems.
        """

        pain_points = set()


        for customer in research.get(
            "target_audience",
            []
        ):

            for pain in customer.get(
                "pain_points",
                []
            ):

                pain_points.add(pain)


        return list(pain_points)



    def _identify_customer_needs(
            self,
            research,
            idea
    ):

        """
        Maps customer needs with startup features.
        """

        needs = []


        features = idea.get(
            "proposed_features",
            []
        )


        for customer in research.get(
            "target_audience",
            []
        ):

            for need in customer.get(
                "needs",
                []
            ):

                needs.append({

                    "need": need,

                    "supported":

                        need.lower()
                        in
                        [
                            feature.lower()
                            for feature in features
                        ]

                })


        return needs



    def _analyze_customer_sentiment(
            self,
            research
    ):

        """
        Analyses customer feedback sentiment.
        """

        positive = 0
        negative = 0


        for feedback in research.get(
            "customer_feedback",
            []
        ):

            sentiment = feedback.get(
                "sentiment",
                ""
            ).lower()


            if sentiment == "positive":

                positive += 1


            elif sentiment == "negative":

                negative += 1



        if positive > negative:

            result = "Positive"

        elif negative > positive:

            result = "Negative"

        else:

            result = "Neutral"



        return {

            "overall_sentiment": result,

            "positive_feedback": positive,

            "negative_feedback": negative

        }



    def _analyze_feature_demand(
            self,
            idea,
            research
    ):

        """
        Finds customer demand for startup features.
        """

        result = []


        requested = research.get(
            "requested_features",
            []
        )


        for feature in idea.get(
            "proposed_features",
            []
        ):


            count = requested.count(feature)


            result.append({

                "feature": feature,

                "demand": count,


                "priority":

                    "High"
                    if count >= 5

                    else

                    "Medium"
                    if count >= 2

                    else

                    "Low"

            })


        return result
    # ==========================================================
    # CUSTOMER SCORING FUNCTIONS
    # ==========================================================


    def _calculate_customer_validation_score(
            self,
            personas,
            pain_points,
            needs,
            sentiment
    ):

        score = 0


        if personas:

            score += 25


        if pain_points:

            score += 25


        if needs:

            score += 25


        if sentiment.get(
            "overall_sentiment"
        ) == "Positive":

            score += 25



        return min(
            score,
            100
        )



    def _calculate_customer_confidence(
            self,
            research
    ):

        score = 0


        if research.get(
            "target_audience"
        ):

            score += 30


        if research.get(
            "customer_feedback"
        ):

            score += 30


        if research.get(
            "requested_features"
        ):

            score += 20


        if research.get(
            "customer_surveys"
        ):

            score += 20



        if score >= 80:

            return "High"


        elif score >= 50:

            return "Medium"


        return "Low"



    def _generate_customer_summary(
            self,
            personas,
            pain_points,
            validation_score,
            confidence
    ):

        return (

            f"{len(personas)} customer personas identified. "

            f"{len(pain_points)} customer pain points discovered. "

            f"Customer validation score is "
            f"{validation_score}/100. "

            f"Confidence level: {confidence}."

        )
    # =====================================================
    # A2A TOOL METHODS
    # =====================================================


    def get_customer_summary(self):

        return self.context.get(
            "customer_analysis",
            {}
        )



    def get_customer_personas(self):

        return self.context.get(
            "customer_analysis",
            {}
        ).get(
            "personas",
            []
        )



    def get_customer_pain_points(self):

        return self.context.get(
            "customer_analysis",
            {}
        ).get(
            "pain_points",
            []
        )



    def get_customer_needs(self):

        return self.context.get(
            "customer_analysis",
            {}
        ).get(
            "needs",
            []
        )



    def get_feature_demand(self):

        return self.context.get(
            "customer_analysis",
            {}
        ).get(
            "feature_demand",
            []
        )



    def get_customer_sentiment(self):

        return self.context.get(
            "customer_analysis",
            {}
        ).get(
            "sentiment",
            {}
        )



    def calculate_customer_validation_score(self):

        return self.context.get(
            "customer_analysis",
            {}
        ).get(
            "validation_score",
            0
        )



    def get_customer_confidence(self):

        return self.context.get(
            "customer_analysis",
            {}
        ).get(
            "confidence",
            "Low"
        )