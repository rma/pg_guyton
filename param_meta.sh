#!/bin/sh

for p in A1K A2K A3K A4K A4K2 AARK ADHPAM ADHTC AH11 AH9 AHMNAR AHTHM ALCLK ALDMM AMCSNS AMKM AMKMUL AMNAM AMT ANCSNS ANMALD ANMAM ANMEM ANMKEM ANMNAM ANMSLT ANMTM ANPTC ANPXAF ANT ANUM ANV ANY AUC1 AUK AUMK1 AUN1 AUS AUTOK AUTOSN AUV AUX BAROTC CFC CNR CPF CPR CV DHDTR DIURET DTNAR EARK GFLC HM6 HM8 HSL HSR HTAUML HYL KID KORGN KORTC LPPR MDFLKM MDFLWX NID O2A O2CHMO O2M OMM PCR PM5 POR QRF RABSC RFABDM RFABKM RNAGTC RNAUGN RTPPR RTPPRS RTSPRS RVSM SR SR2 SRK SRK2 TENSTC TSSLML TSSLTC TVDDL U VIDML VNTSTM VPTISS VV9; do
  ./describe.sh $p
done

