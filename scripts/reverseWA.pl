#/usr/bin/env perl
# stephen grimes, sgrimes@ldc.upenn.edu

# takes a tool-format .wa file that is A-B and makes it B-A by 
# switching source and translation roles. So lanaguages A and B swap
# sides of the tool.

open(WA,"<$ARGV[0]") || die "could not open $ARGV[0]\n";

while (<WA>) {

   if (/^<sentence/) {
       print;
       @source = ();
       @translation = ();
   }
   elsif (/<source>/) {
      $is_source = 1;
   }
   elsif (/<\/source>/) {
      $is_source = 0;
   }
   elsif (/<translation>/) {
      $is_translation = 1;
   }
   elsif (/<\/translation>/) {
      $is_translation = 0;
      print "// $trans_line\n";
      print "// $source_line\n";
      print "<source>\n";
      for ($i=0;$i<=$#translation;$i++) {
	  print "$translation[$i]\n";
      }
      print "</source>\n";
      print "<translation>\n";
      for ($i=0;$i<=$#source;$i++) {
          print "$source[$i]"
      }
      print "</translation>\n";
   }
   elsif ($is_source == 1) {
       push(@source, $_);
       /\d+ (\S+) : /;
       $source_line = $source_line . $1 . " ";
   }
   elsif ($is_translation == 1) {
       chomp;
       push(@translation, $_);
       /\d+ (\S+) :/;
       $trans_line = $trans_line . $1 . " ";

   }
   elsif (/<alignment>/) {
      $alignment = 1;
      print;
   }
   elsif (/<\/alignment>/) {
       $alignment = 0;
       print;
   }
   elsif ($alignment == 1) {
       /(.*?) \/\/ (\w{3}) \/\/(.*)/;
       $align = $1;
       $link_type = $2;
       $tokens = $3;

       $align =~ s/(.*) <==> (.*)/$2 <==> $1/;
       $tokens =~ s/(.*) <==> (.*)/$2 <==> $1/;
       print "$align // $link_type // $tokens\n";
 

   }
   elsif (/Comment:/) {
       print;
   }
   elsif (/<\/sentence>/) {
       print "</sentence>\n\n\n";
   }
}
