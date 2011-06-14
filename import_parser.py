"""
This module parses experiment results.

Simulation results are recorded in the following (tab-delimited) format:

\#individuX
<initial parameter values>
<param num> <delta>
[PA time <variables>] for time in: [4wks, +5min, +1hr, +1d, +1w, +4w]
[any number of blank lines]

"""

parameter_list = ("a1k, a2k, a3k, a4k, a4k2, aark, adhpam, adhtc, ah10, ah11, "
"ah9, ahmnar, ahthm, alclk, aldmm, amcsns, amkm, amkmul, amnam, amt, ancsns, "
"anmald, anmam, anmem, anmkem, anmnam, anmslt, anmtm, anptc, anpxaf, ant, "
"anum, anv, any, auc1, audmp, auk, aumk1, aun1, aus, autogn, autok, autosn, "
"auv, aux, barotc, cfc, cnr, cpf, cpr, cv, dhdtr, diuret, dr, dtnar, eark, "
"exc, excml, exe, fis, gflc, gfndmp, gppd, hm6, hm8, hmk, hmtrns, hsl, hsr, "
"htauml, hyl, kid, korgn, kortc, lppr, mdflkm, mdflw2, mdflwx, nid, o2a, "
"o2chmo, o2m, omm, pcr, pm5, por, pxtp, qrf, rabsc, rcdfpc, rek, rfabdm, "
"rfabdp, rfabkm, rnagtc, rnaugn, rtppr, rtpprs, rtsprs, rvsm, sr, sr2, srk, "
"srk2, tenstc, tsslml, tssltc, tvddl, u, urform, vidml, vntstm, vptiss, vv9, "
"aarll, adhinf, adhkll, adhkul, adhpul, adhvll, adhvul, aldinf, aldkns, "
"am1ll, am1ul, amm1lm, amm4, amnall, amnaul, anginf, angkns, anmarl, anmkel, "
"anmll, anmul, anpxul, anull, anuvm, anxm, ar1lm, ar2lm, arf, aul, aulpm, "
"aum1, aum2, aumax, aumin, auslp, ckeex, cmptss, cn2, cn7, cpk, dtnarl, "
"earll, efafr, excxp, excxp2, gcopf, gfnll, i2, i3, i4, i6, i8, i10, i12, "
"i14, i16, i18, i20, lpde, lpk, mdfl1, mdmp, pa4, paex, pce, pghf, pk2, pl2, "
"pldf, po2adv, pok, pom, pom2, pon, poz, pr1ll, qaolm, raprsp, rar, rcdfdp, "
"rkc, rnauad, rvrs, sta, tensgn, timetr, trnsfs, trpl, vid1, vp1, vtsf, x, z, "
"z4, z5, z6, z7, z10, z11, z12, z13, z14, z16, z18, z19"
).upper().split(", ")
"""The list of parameter names, in the order that they are listed in the
simulation results."""

variable_list = ("i, t, au4, au2, au8, amk, amna, amrbsc, amr, amr1, am1, am, "
"amc, anu, anuvn, anm, mdflw3, angscr, anx, anx1, anpr, anpr1, anc, anpx, "
"anpl, anpr2, anp, anp1, anpc, adhc, adhmk, adhmv, adhna, adhpa, adhpr, adh, "
"adhz, au, au6, auh, aum, aur, ave, pa1, vvr, auo, auc, auc2, aub, a1b, aun, "
"aulp, auttl, dau, au1, rmult1, vrc, hm, hm1, vb, vim, vie, vib, po2am1, hm3, "
"hm4, hm5, hm7, rc1, rc2, rcd, prp, cpp, pc, ppc, vp, vtc, vpd, cppd, dlp, "
"prcd, vtcpl, dpc, dpp, vts, vts2, vts1, dpi, tsp, cpi, dpl, ptcpr, chy, pgh, "
"poshyl, ptc, ptt, pif, pts, pld, vtl, vif, bfm, bfn, myogrs, pa, pamkrn, pla, "
"pra, ppa, pvs, qao, qlo, qro, rpv, rvs, vae, vle, vpe, vre, vve, vbd, vvs, "
"vas, vla, vpa, vra, pam, rad, pamk, pa2, pra1, qrn, pp1, cpa, rpa, pp2, rvm, "
"pla1, qln, pl1, rpt, pgl, qpo, pr1, rvg, qvo, cn3, rv1, pgs, r1, rsn, rsm, "
"fisflo, sysflo, qlo1, hpef, dvs, dpa, das, dla, dra, cna, cke, vec, vtw, ned, "
"amk1, ktotd, ktot, vic, cki, nae, ccd, vid, hmd, dhm, hpl, hpr, nod, kod, "
"vud, rbf, mdflw, par, aumk, anmer, anmar, rnaug1, rnaug2, rnaug3, aar, ear, "
"rr, rfn, efafpr, glpc, apd, glp, pfl, rcprs, rtsppc, rabspr, rfab1, rfab, "
"rfabk, dtnai, dtnara, dtki, anmke, mdflk, dtksc, dtnang, nodn, dtka, kodn, "
"osmopn, vudn, plur, plurc, dturi, urod, amm, pdo, poe, amm1, amm2, aom, pmo, "
"rmo, mmo, ovs, pvo, do2m, qom, p2o, arm, pod, pob, ar1, poa, ar2, poc, ar3, "
"dob, pot, osv, pov, mo2, do2n, qo2, p1o, dfp, ppd, vpf, pcp, ppi, cpn, pos, "
"plf, ppo, ppn, ppz, pfi, dfz, ppr, o2util, alvent, po2alv, rspdfc, o2dfs, "
"dova, o2vtst, o2vts2, do2vad, o2vad1, o2vad2, osa, ova, po2art, pmc, pms, "
"pmp, hr, rtp, svo, vv6, vv7, tvd, sth, ke, ki, atrrfb, atrvfb, ahz, ahy, "
"ah7, gfr, agk, ahk, ahth, amm3, anmsml, anmth, anpinf, anpkns, ar4, "
"ar5, atrfbm, atrvm, au6a, au6b, au6c, aurg, autoC, auy, crrflx, gbl, gfn, "
"glpca, hkm, i1, i5, i9, i11, i13, i15, i17, i19, i21, korner, korren, lvm, "
"mdflw1, osmop1, pa3, pcd, pgp, pgv, po2amb, po2ar1, ptfl, ram, rfabd, rfabx, "
"rfcdft, rmult, rnaull, rnauul, rps, tens, tens1, tens2, trnstm, trrbc, tvz, "
"vg, vud1, vud2"
).upper().split(", ")
"""The list of variable names, in the order that they are listed in the
simulation results."""

import csv
import sys

def import_parser(results):
    """
    The import_parser generator parses the results of individual simulations
    and returns the parsed data in the following form:

    (line_list, first_line_number, last_line_number)

    """
    reader = csv.reader(results, delimiter='\t')
    line_num = 1
    # parse the results for a single simulation
    for line in reader:
        # find the first non-empty line
        while len(line) < 1:
            line = reader.next()
            line_num += 1
        lines = []
        first_line = line_num

        # read in all lines until the next empty line
        while len(line) >= 1:
            lines.append(line)
            line = reader.next()
            line_num += 1
        last_line = line_num

        # return the lines, and the range of line numbers encompassed
        yield (lines, first_line, last_line)

def parse(results, callback, callback_data=None, err_callback=None, warn=False):
    """
    This function parses all of the simulations in results, passing the
    details of each simulation in turn to the callback function. The
    callback function is called with the following arguments:

    (callback_data, initial_parameters, delta_parameter, delta_increment,
    variables_pre_delta, variables_post_deltas, simulation_count)

    If an error occurs, the err_callback function will be called. If warn
    is set to True, warnings will be printed to sys.stderr when numerical
    values are forcibly rounded.

    """
    count = 0

    for (result, fst_line, lst_line) in import_parser(results):
        # there should be nine lines in all
        if len(result) != 9:
            if error_callback is not None:
                error_callback(result, fst_line, lst_line)
            else:
                msg = "ERROR: lines", fst_line, "-", lst_line
                print >> sys.stderr, msg
                continue

        #
        # The double precision type typically has a range of around
        # 1e-307 to 1e+308 with a precision of at least 15 digits.
        #
        # http://www.postgresql.org/docs/8.4/static/datatype-numeric.html
        #
        def clip_val(s):
            x = float(s)
            if x == 0:
                return x
            elif abs(x) < 1e-300:
                return 0
            elif x > 1e300:
                if warn:
                    print >> sys.stderr, ("Warning: rounding '%s' down" % (s,))
                return 1e300
            elif x < -1e300:
                if warn:
                    print >> sys.stderr, ("Warning: rounding '%s' up" % (s,))
                return -1e300
            else:
                return x

        # parse the results
        try:
            init_params = map(clip_val, result[1])
            if len(init_params) != len(parameter_list):
                msg = "ERROR:", len(init_params), "parameters"
                print >> sys.stderr, msg
                continue
            delta_line = result[2]
            if len(delta_line) != 2:
                msg = "ERROR: delta line has", delta_line, "fields"
                print >> sys.stderr, msg
                continue
            else:
                delta_param = int(delta_line[0])
                delta_incr = clip_val(delta_line[1])
            pre_delta = map(clip_val, result[3])
            if len(pre_delta) != len(variable_list):
                msg = "ERROR:", len(pre_delta), "variables"
                print >> sys.stderr, msg
                continue
            post_deltas = map(lambda xs: map(clip_val, xs), result[4:9])
            if len(post_deltas) != 5:
                msg = "ERROR:", len(post_deltas), "lines after delta"
                print >> sys.stderr, msg
            for pd in post_deltas:
                if len(pd) != len(variable_list):
                    msg = "ERROR:", len(pd), "variables"
                    print >> sys.stderr, msg
                    continue
            count = count + 1
        except ValueError:
            msg = "ERROR: invalid number in lines", fst_line, "-", lst_line
            print >> sys.stderr, msg
            continue

        # send the result to the callback
        callback(callback_data, init_params, delta_param, delta_incr,
                 pre_delta, post_deltas, count)

    return count

def var(n):
    """Returns the name of the nth variable."""
    return variable_list[n]

def par(n):
    """Returns the name of the nth parameter."""
    return parameter_list[n]

def var_list():
    """Returns the list of variable names."""
    return variable_list

def par_list():
    """Returns the list of parameter names."""
    return parameter_list

def var_of_interest(name):
    """Returns true if the variable of the given name is interesting."""
    # GFR is the last interesting variable
    if name in variable_list:
        return variable_list.index(name) <= variable_list.index('GFR')
    else:
        print >> sys.stderr, "Unknown variable", name
        sys.exit()

def par_of_interest(name):
    """Returns true if the parameter of the given name is interesting."""
    # VV9 is the last interesting parameter
    if name in parameter_list:
        return parameter_list.index(name) <= parameter_list.index('VV9')
    else:
        print >> sys.stderr, "Unknown parameter", name
        sys.exit()
