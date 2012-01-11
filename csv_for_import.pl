#!/usr/bin/env perl

#
# NOTE: build the POD documentation with the following command.
#
#     pod2html --infile=csv_for_import.pl --outfile=csv_for_import.html
#              --title=csv_for_import.pl --noindex
#

=pod

=head1 NAME

csv_for_import.pl - CSV conversion for importing data into PostgreSQL

=head1 SYNOPSIS

Usage:

    csv_for_import.pl [-v, --verbose] [-f FILE, --file=FILE]

Example:

    # csv_for_import.pl -v -f data1.txt -f data2.txt
    # cat individuals.csv | psql --dbname DATABASE \
      -c "COPY individual (id, perturbed) FROM STDIN WITH CSV"
    # cat indiv_params.csv | psql --dbname DATABASE \
      -c "COPY indiv_params (individual, parameter, value) FROM STDIN WITH CSV"
    # cat indiv_vars.csv | psql --dbname DATABASE \
      -c "COPY indiv_vars (individual, variable, value) FROM STDIN WITH CSV"

=head1 DESCRIPTION

This script parses one or more delta-perturbation simulation files, and
creates CSV files (F<individuals.csv>, F<indiv_params.csv>, F<indiv_vars.csv>)
that can be imported into a PostgreSQL database.

=head1 DOCUMENTATION

=over 1

=item @param_list

The ordered list of all model parameters.

=item @delta_list

The list of all perturbed model parameters.

=item @var_list

The ordered list of all model variables.

=item index_of($item, \@list)

Returns the index of $item in @list, or C<scalar(@list)>.

=item interesting_param($param)

Returns true if the parameter is I<interesting>.

=item interesting_var($var)

Returns true if the variable is I<interesting>.

=item parse_individual(\@record)

Parses the sequence of nine lines that describe one perturbation simulation,
and returns a reference to a hash that contains the parsed results.

=item write_indiv($row, $is_perturbed, $output_file)

Writes the details of an individual to $output_file.

=item write_row($row, \@data, $output_file)

Writes a line of data to $output_file.

=item test_interest()

Runs some simple tests on C<interesting_param()> and C<interesting_var()>.

=item main()

The entry-point of the script.

=back

=head1 AUTHOR

Robert Moss

=head1 COPYRIGHT

This program is distributed under the 3-clause BSD license.

=cut

use strict;
use warnings;

use Getopt::Long;

my @param_list = map { uc($_) } qw(
    a1k a2k a3k a4k a4k2 aark adhpam adhtc ah10 ah11 ah9 ahmnar ahthm alclk
    aldmm amcsns amkm amkmul amnam amt ancsns anmald anmam anmem anmkem
    anmnam anmslt anmtm anptc anpxaf ant anum anv any auc1 audmp auk aumk1
    aun1 aus autogn autok autosn auv aux barotc cfc cnr cpf cpr cv dhdtr
    diuret dr dtnar eark exc excml exe fis gflc gfndmp gppd hm6 hm8 hmk
    hmtrns hsl hsr htauml hyl kid korgn kortc lppr mdflkm mdflw2 mdflwx nid
    o2a o2chmo o2m omm pcr pm5 por pxtp qrf rabsc rcdfpc rek rfabdm rfabdp
    rfabkm rnagtc rnaugn rtppr rtpprs rtsprs rvsm sr sr2 srk srk2 tenstc
    tsslml tssltc tvddl u urform vidml vntstm vptiss vv9 aarll adhinf adhkll
    adhkul adhpul adhvll adhvul aldinf aldkns am1ll am1ul amm1lm amm4 amnall
    amnaul anginf angkns anmarl anmkel anmll anmul anpxul anull anuvm anxm
    ar1lm ar2lm arf aul aulpm aum1 aum2 aumax aumin auslp ckeex cmptss cn2
    cn7 cpk dtnarl earll efafr excxp excxp2 gcopf gfnll i2 i3 i4 i6 i8 i10
    i12 i14 i16 i18 i20 lpde lpk mdfl1 mdmp pa4 paex pce pghf pk2 pl2 pldf
    po2adv pok pom pom2 pon poz pr1ll qaolm raprsp rar rcdfdp rkc rnauad
    rvrs sta tensgn timetr trnsfs trpl vid1 vp1 vtsf x z z4 z5 z6 z7 z10 z11
    z12 z13 z14 z16 z18 z19);

my @delta_list = map { uc($_) } qw(
    a1k a2k a3k a4k a4k2 aark adhpam adhtc ah11 ah9  ahmnar ahthm alclk
    aldmm amcsns amkm amkmul amnam amt ancsns anmald anmam anmem anmkem
    anmnam anmslt anmtm anptc anpxaf ant  anum anv any auc1 auk aumk1 aun1
    aus autok autosn auv aux  barotc cfc cnr cpf cpr cv dhdtr diuret dtnar
    eark gflc hm6 hm8 hsl hsr htauml hyl kid korgn kortc lppr mdflkm mdflwx
    nid o2a  o2chmo o2m omm pcr pm5 por qrf rabsc rfabdm rfabkm rnagtc
    rnaugn rtppr rtpprs rtsprs rvsm sr sr2 srk srk2 tenstc tsslml tssltc
    tvddl u vidml vntstm vptiss vv9);

my @var_list = map { uc($_) } qw(
    i t au4 au2 au8 amk amna amrbsc amr amr1 am1 am amc anu anuvn anm mdflw3
    angscr anx anx1 anpr anpr1 anc anpx anpl anpr2 anp anp1 anpc adhc adhmk
    adhmv adhna adhpa adhpr adh adhz au au6 auh aum aur ave pa1 vvr auo auc
    auc2 aub a1b aun aulp auttl dau au1 rmult1 vrc hm hm1 vb vim vie vib
    po2am1 hm3 hm4 hm5 hm7 rc1 rc2 rcd prp cpp pc ppc vp vtc vpd cppd dlp
    prcd vtcpl dpc dpp vts vts2 vts1 dpi tsp cpi dpl ptcpr chy pgh poshyl
    ptc ptt pif pts pld vtl vif bfm bfn myogrs pa pamkrn pla pra ppa pvs qao
    qlo qro rpv rvs vae vle vpe vre vve vbd vvs vas vla vpa vra pam rad pamk
    pa2 pra1 qrn pp1 cpa rpa pp2 rvm pla1 qln pl1 rpt pgl qpo pr1 rvg qvo
    cn3 rv1 pgs r1 rsn rsm fisflo sysflo qlo1 hpef dvs dpa das dla dra cna
    cke vec vtw ned amk1 ktotd ktot vic cki nae ccd vid hmd dhm hpl hpr nod
    kod vud rbf mdflw par aumk anmer anmar rnaug1 rnaug2 rnaug3 aar ear rr
    rfn efafpr glpc apd glp pfl rcprs rtsppc rabspr rfab1 rfab rfabk dtnai
    dtnara dtki anmke mdflk dtksc dtnang nodn dtka kodn osmopn vudn plur
    plurc dturi urod amm pdo poe amm1 amm2 aom pmo rmo mmo ovs pvo do2m qom
    p2o arm pod pob ar1 poa ar2 poc ar3 dob pot osv pov mo2 do2n qo2 p1o dfp
    ppd vpf pcp ppi cpn pos plf ppo ppn ppz pfi dfz ppr o2util alvent po2alv
    rspdfc o2dfs dova o2vtst o2vts2 do2vad o2vad1 o2vad2 osa ova po2art pmc
    pms pmp hr rtp svo vv6 vv7 tvd sth ke ki atrrfb atrvfb ahz ahy ah7 gfr
    agk ahk ahth amm3 anmsml anmth anpinf anpkns ar4 ar5 atrfbm atrvm au6a
    au6b au6c aurg autoC auy crrflx gbl gfn glpca hkm i1 i5 i9 i11 i13 i15
    i17 i19 i21 korner korren lvm mdflw1 osmop1 pa3 pcd pgp pgv po2amb
    po2ar1 ptfl ram rfabd rfabx rfcdft rmult rnaull rnauul rps tens tens1
    tens2 trnstm trrbc tvz vg vud1 vud2);

sub index_of($@) {
    my ($item, $list) = @_;

    my $index = 0;
    ++$index until $$list[$index] eq $item or $index > $#$list;
    return $index;
}

sub interesting_param ($) {
    my ($param) = @_;

    if (index_of($param, \@param_list) <= index_of('VV9', \@param_list)) {
        return 1;
    } else {
        return 0;
    }
}

sub interesting_var ($) {
    my ($var) = @_;

    if (index_of($var, \@var_list) <= index_of('GFR', \@var_list)) {
        return 1;
    } else {
        return 0;
    }
}

sub parse_individual (@) {
    my @record = @{$_[0]};

    my %output = ();

    $output{'params'} = [ grep(length, split(/\s/, $record[1])) ];
    my @deltas = grep(length, split(/\s/, $record[2]));
    $output{'delta_param'} = $deltas[0];
    $output{'delta_incr'} = $deltas[1];
    $output{'vars_pre'} = [ grep(length, split(/\s/, $record[3])) ];
    $output{'vars_1m'} = [ grep(length, split(/\s/, $record[4])) ];
    $output{'vars_1h'} = [ grep(length, split(/\s/, $record[5])) ];
    $output{'vars_1d'} = [ grep(length, split(/\s/, $record[6])) ];
    $output{'vars_1w'} = [ grep(length, split(/\s/, $record[7])) ];
    $output{'vars_4w'} = [ grep(length, split(/\s/, $record[8])) ];

    return \%output;
}

sub write_indiv($$$) {
    my ($row_ix, $perturbed, $indiv_fh) = @_;

    if ($perturbed) {
        $perturbed = 't';
    } else {
        $perturbed = 'f';
    }

    print $indiv_fh $row_ix . "," . $perturbed . "\n";
}

sub write_row($$$) {
    my ($row_ix, $data, $output_fh) = @_;
    my @data = @$data;

    for my $i (0 .. $#data) {
        print $output_fh $row_ix . "," . $i . "," . $data[$i] . "\n";
    }
}

sub process_file($$$$$) {
    my ($input_file, $row_ix, $i_fh, $p_fh, $v_fh) = @_;

    my @record = ();

    open INPUTFILE, $input_file or die $!;

    while (<INPUTFILE>) {
        @record = ();

        my $line = $_;
        chomp($line);
        push(@record, $line);
        for (my $i = 1; $i < 10; $i++) {
            chomp($line = <INPUTFILE>);
            push(@record, $line);
        }

        my $output = parse_individual(\@record);

        my $init_params = $$output{'params'};
        my @init_params = @$init_params;
        my @delta_params = @init_params;
        $delta_params[$$output{'delta_param'}] += $$output{'delta_incr'};

        my $init_vars = $$output{'vars_pre'};
        my @init_vars = @$init_vars;
        my $delta_vars = $$output{'vars_4w'};
        my @delta_vars = @$delta_vars;

        write_indiv($row_ix, 0, $i_fh);
        write_row($row_ix, \@init_params, $p_fh);
        write_row($row_ix, \@init_vars, $v_fh);
        $row_ix++;
        write_indiv($row_ix, 1, $i_fh);
        write_row($row_ix, \@delta_params, $p_fh);
        write_row($row_ix, \@delta_vars, $v_fh);
        $row_ix++;
    }

    return $row_ix;
}

sub test_interest {
    print 'VV9' . " : " . interesting_param('VV9') . "\n";
    print 'AARLL' . " : " . interesting_param('AARLL') . "\n";
    print 'GFR' . " : " . interesting_var('GFR') . "\n";
    print 'AGK' . " : " . interesting_var('AGK') . "\n";
}

sub main {
    my @input_files = ();
    my $verbose = 0;

    GetOptions("file=s"   => \@input_files,
               "verbose!" => \$verbose);

    my $indiv_file = "individuals.csv";
    my $param_file = "indiv_params.csv";
    my $var_file = "indiv_vars.csv";

    open my $i_fh, '>', $indiv_file or die $!;
    open my $p_fh, '>', $param_file or die $!;
    open my $v_fh, '>', $var_file or die $!;

    my $row_ix = 0;
    my $prev_ix = 0;

    eval {
        for my $input_file (@input_files) {
            if ($verbose) {
                print "Processing '" . $input_file . "' ...\n";
            }
            $prev_ix = $row_ix;
            $row_ix = process_file($input_file, $row_ix, $i_fh, $p_fh, $v_fh);
            if ($verbose) {
                print "\t" . ($row_ix - $prev_ix) . " individuals.\n";
            }
        }
    } or do {
        if ($@) {
            print "ERROR: " . $@ . "\n";
        }
    };

    if ($verbose) {
        print "Cleaning up ... ";
    }
    close($i_fh);
    close($p_fh);
    close($v_fh);
    if ($verbose) {
        print "done\n";
    }
}

main();
