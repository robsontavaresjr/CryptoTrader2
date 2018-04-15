# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 09:41:30 2015

@author: Aluno - Joao
"""


def workmemory(location):
    arq = file(location, 'rU')
    lines = arq.readlines()
    arq.close()

    wm = {}

    for line in lines:

        line = line.upper()
        line = line.replace("\n", "")

        if line == "":

            pass

        else:

            split = line.split("=")

            if len(split) == 2:

                ref, val = split

                if val == "TRUE":

                    val = True

                elif val == "FALSE":

                    val = False

                elif val == "":

                    val = None

                else:

                    val = eval(val)

                wm[ref] = val

            else:

                raise Exception("Erro de leitura do WorkMemory")
    return wm


def write_workmemory(wm, location):
    arq = open(location, 'w')

    for eachKey in wm.keys():

        val = wm[eachKey]

        if val is None:
            val = ''
        else:
            val = repr(val)

        arq.write(eachKey + '=' + val + "\n")

    arq.close()


def str2rule(rulestr):
    if rulestr == '':

        return None

    else:

        rulestr = rulestr.upper()

        symbs = {" TRUE ": " True ", " FALSE ": " False ", " I ": " None ", " AND ": " and ", " OR ": " or ",
                 "(": " ( ", ")": " ) "}

        # Retira IF

        if rulestr[0] != " ":
            rulestr = " " + rulestr

        rulestr = rulestr.replace(" IF ", "")

        # Garante que inicia com espaco vazio

        if rulestr[0] != " ":
            rulestr = " " + rulestr

        # Garante que regra termina com espaco vazio

        if rulestr[-1] != " ":
            rulestr += " "

        for eachSymb in symbs.keys():

            if eachSymb in rulestr:
                rulestr = rulestr.replace(eachSymb, symbs[eachSymb])

        # Separacao Antecedente/Consequente

        if " THEN " in rulestr:

            antecedente, consequente = rulestr.split(" THEN ")
            consequentelist = []

            # Separacao de multiplos consequentes

            if " and " in consequente:

                consequentes = consequente.split(" and ")

                for eachConsequente in consequentes:

                    Unpack = eachConsequente.split(" = ")

                    if len(Unpack) == 2:

                        ref, value = Unpack

                    else:

                        ref = Unpack[0]
                        value = ""

                        for i in xrange(1, len(Unpack)):

                            if i != len(Unpack) - 1:

                                value += Unpack[i] + " = "

                            else:

                                value += Unpack[i]

                    ref = ref.replace(" ", "")

                    consequentelist.append([ref, value])
            else:

                ref, value = consequente.split(" = ")
                ref = ref.replace(" ", "")

                consequentelist.append([ref, value])

        else:

            consequentelist = []
            antecedente = rulestr

        # Garantir que Antecedente termine com espaco

        if antecedente[-1] != " ":
            antecedente += " "

        rule = [antecedente, consequentelist]

        return rule


def execrule(rule, wm, ret_exec=False, ret_back=False):
    track = {}

    if rule is None:

        print "Empty rule."
        return wm

    else:

        antecedente = rule[0]
        consequente = rule[1]

        for eachKey in wm.keys():

            if eachKey in antecedente:

                if ret_back:
                    track[eachKey] = wm[eachKey]

                antecedente = antecedente.replace(" " + eachKey + " ", " " + repr(wm[eachKey]) + " ")

            else:

                pass

        try:

            alrdy_exec = False

            if eval(antecedente) == True:

                alrdy_exec = True

                for eachConsequente in consequente:

                    if eachConsequente[0] in wm.keys():

                        wm[eachConsequente[0]] = eval(eachConsequente[1])

                    else:

                        print "Variable added to the workmemory"
                        wm[eachConsequente[0]] = eval(eachConsequente[1])

            if ret_exec:
                return wm, alrdy_exec
            if ret_back:
                return wm, track
            else:
                return wm

        except:

            print antecedente
            print consequente

            raise Exception("Nao e possivel ler Antecedente")


def read_kb(location):
    rules = []
    ret_vars = False

    arq = file(location, 'rU')
    lines = arq.readlines()

    symbs = {" TRUE ": " True ", " FALSE ": " False ", " I ": " None ", " AND ": " and ", " OR ": " or ", "(": " ( ",
             ")": " ) "}

    for line in lines:

        line = line.replace("\n", "")
        line = line.upper()

        if line != "":

            if line[0] == ':':

                line = line[1:]
                line = line.replace(' ', "")
                variables_references = line.split(',')
                ret_vars = True

            else:

                for eachSymb in symbs.keys():
                    line = line.replace(eachSymb, symbs[eachSymb])

                rule = str2rule(line)
                rules.append(rule)

    if ret_vars:
        return variables_references, rules
    else:
        return [], rules


def clear_wm(wm):
    for eachKey in wm.keys():
        wm[eachKey] = None

    return wm
