#!/usr/bin/env perl
# stephen grimes, sgrimes@ldc.upenn.edu


# given two parallel text files, create a tool-format .wa file
# two text files but contain same number of lines
# one sentence/translation per line


# sample usage (source.txt, translation.txt existing):
#
# perl makeWA.pl source.txt translation.txt NewAlignmentFile.wa


if ($#ARGV != 2) {die "Usage: sourceSentences targetSentences NewAlignmentFile.wa\n"}

open (SOURCE, "<$ARGV[0]") || die "could not open source $ARGV[0]\n";
open (TARGET, "<$ARGV[1]") || die "could not open translation $target\n";
@source = <SOURCE>;
@target = <TARGET>;
close SOURCE;
close TARGET;


if ($#source != $#target) {
die "Error:\n \$#source:$#source, \$#trans:$#target\n";}

open (OUT, ">$ARGV[2]") || die "could not open out $out\n";

for ($sent=0;$sent<=$#source;$sent++) {
    # delete leading and trailing spaces from sentences:
    $source[$sent] =~ s/^ *//g;
    $source[$sent] =~ s/ *$//g;
    $target[$sent] =~ s/^ *//g;
    $target[$sent] =~ s/ *$//g;

    $sent_num = $sent + 1;
    print OUT "<sentence id=\"$sent_num\" status=\"\">\n";
    if ($source[$sent] =~ /\n/) {
	print OUT "// $source[$sent]"}
    else {
	print OUT "// $source[$sent]\n"}
    if ($target[$sent] =~ /\n/) {
	print OUT "// $target[$sent]";}
    else {
	print OUT "// $target[$sent]\n"}
    print OUT "<source>\n";
    @s = split (' ', $source[$sent]);
    for ($i=0;$i<=$#s;$i++) {
	$tok_num = $i+1;
	$s[$i] =~ s/\s+$//;
	if($s[$i] =~ / +/) {die "cmn.tkn file Line: $sent_num, Token: $tok_num contains space(s). WA file creation failed.\n"}
	if(!$s[$i] && !($s[$i] =~ /^0$/)) {die "cmn.tkn file Line: $sent_num, Token: $tok_num generates empty token(s). WA file creation failed.\n"}
	print OUT $i+1 . " $s[$i] : \n";
    }
    print OUT "</source>\n";
    print OUT "<translation>\n";
    @t = split (' ', $target[$sent]);
    for ($i=0;$i<=$#t;$i++) {
	$tok_num = $i+1;
	$t[$i] =~ s/\s+$//;
	if($t[$i] =~ / +/) {die "eng.tkn file Line: $sent_num, Token: $tok_num contains space(s). WA file creation failed.\n"}
	if(!$t[$i] && !($t[$i] =~ /^0$/)) {die "eng.tkn file Line: $sent_num, Token: $tok_num generates empty token(s). WA file creation failed.\n"}
	print OUT $i+1 . " $t[$i] : \n";
    }
    print OUT "</translation>\n";
    print OUT "<alignment>\n";
    print OUT "</alignment>\n";
    print OUT "Comment: \n";
    print OUT "</sentence>\n\n\n";
}

print "Success: $out\n";
