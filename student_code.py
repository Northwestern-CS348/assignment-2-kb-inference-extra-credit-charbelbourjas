import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment

    def kb_explain(self, fact_or_rule):
        """
        Explain where the fact or rule comes from

        Args:
            fact_or_rule (Fact or Rule) - Fact or rule to be explained

        Returns:
            string explaining hierarchical support from other Facts and rules
        """
        ####################################################
        # Student code goes here
        indent = 0
        explain = ""

        if isinstance(fact_or_rule, Fact):
            curr = None
            curr = self._get_fact(fact_or_rule)

            if(curr == None):
                explain = "Fact is not in the KB"
                return explain

            else:
                explain = explain + "fact: "+ str(curr.statement)

                if curr.asserted:
                    explain = explain + " ASSERTED"
                explain = explain + '\n'
                indent = indent + 1

                if len(curr.supported_by) > 0:
                    for supportive in curr.supported_by:
                        explain = explain + self.helpme(supportive, indent)

                return explain

        elif isinstance(fact_or_rule, Rule):
            curr = None
            curr = self._get_rule(fact_or_rule)

            if (curr == None):
                explain = "Rule is not in the KB"
                return explain

            else:
                explain = explain + "rule: ("
                explain = explain + str(curr.lhs[0])

                for left in curr.lhs[1:]:
                    explain = explain + ", " + str(left)
                explain = explain + ") -> " + str(curr.rhs)

                if curr.asserted:
                    explain = explain + " ASSERTED"
                explain = explain + '\n'
                indent = indent + 1

                if len(curr.supported_by) > 0:
                    for i in curr.supported_by:
                        explain = explain + self.helpme(i, indent)
                return explain
        else:
            return False

    def helpme(self, current_fact_or_rule, indent):
        explain = ""
        indent_new = indent

        for i in range(indent_new):
            explain = explain + "  "
        explain = explain + "SUPPORTED BY" + '\n'
        indent_new = indent_new + 1

        for i in range(indent_new):
            explain = explain + "  "
        explain = explain + "fact: "
        explain = explain + str(current_fact_or_rule[0].statement)

        if current_fact_or_rule[0].asserted:
            explain = explain + " ASSERTED"
        explain = explain + '\n'

        if len(current_fact_or_rule[0].supported_by) > 0:
            for supported in current_fact_or_rule[0].supported_by:
                explain = explain + self.helpme(supported, indent_new + 1)

        for i in range(indent_new):
            explain = explain + "  "
        explain = explain + "rule: ("
        explain = explain + str(current_fact_or_rule[1].lhs[0])

        for left in current_fact_or_rule[1].lhs[1:]:
            explain = explain + ", " + str(left)
        explain = explain + ") -> " + str(current_fact_or_rule[1].rhs)

        if current_fact_or_rule[1].asserted:
            explain = explain + " ASSERTED"
        explain = explain + '\n'

        if len(current_fact_or_rule[1].supported_by) > 0:
            for supported in current_fact_or_rule[1].supported_by:
                explain = explain + self.helpme(supported, indent_new + 1)

        return explain



class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment
