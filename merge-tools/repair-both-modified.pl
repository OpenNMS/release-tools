#!/usr/bin/perl -w

use strict;
use warnings;

use File::Copy;
use File::Slurp;

my $filelist = `git status`;
my $DEBUG = 0;

my $search = shift @ARGV;
my $replace = shift @ARGV;

my @files = qw();

for my $line (split(/\r?\n/, $filelist)) {
	if ($line =~ /pom\.xml/ and $line =~ /both modified:\s*(.*?)\s*$/) {
		push(@files, $1);
	}
}

for my $file (@files) {
	print "$file\n";

	my $text = read_file($file);

	my $in_keeper = 0;
	my $in_remove = 0;

	if (not $DEBUG) {
		open (FILEOUT, '>' . $file . '.new') or die "Can't write to $file.new: $!\n";
	}

	for my $line (split(/\r?\n/, $text)) {
		my $do_print = 0;
		if ($in_keeper == 0 and $in_remove == 0) {
			if ($line =~ /^<<<<<<< /) {
				$in_keeper = 1;
			} else {
				$do_print = 1;
			}
		} elsif ($in_keeper) {
			if ($line =~ /^=======\s*$/) {
				$in_keeper = 0;
				$in_remove = 1;
			} else {
				$do_print = 1;
			}
		} elsif ($in_remove) {
			if ($line =~ /^>>>>>>> /) {
				$in_remove = 0;
			} else {
				$do_print = 0;
			}
		} else {
			print STDERR "$do_print $in_keeper $in_remove UNKNOWN STATE!!!\n";
		}

		my $output_line = $line;
		if (defined $search and defined $replace) {
			$output_line =~ s/${search}/${replace}/g;
		}

		if ($DEBUG) {
			print "$do_print $in_keeper $in_remove $output_line\n";
		} elsif ($do_print) {
			print FILEOUT $output_line, "\n";
		}
	}

	if (not $DEBUG) {
		close (FILEOUT) or die "Can't close $file.new: $!\n";

		move($file . '.new', $file) or die "failed to move $file.new to $file: $!\n";
		system("git add '$file'") == 0 or die "failed to git add $file: $!\n";
	}
}
