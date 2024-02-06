#!/usr/bin/perl

use strict;
use warnings;
use File::Path qw(make_path);
use JSON;
use Getopt::Long;

sub check_os {
    return uc $^O;
}

sub check_dir {
    my $os_type = check_os();
    my $dir;
    if ($os_type eq 'LINUX' || $os_type eq 'UNIX') {
        $dir = "/etc/zabbix/scripts";
    } elsif ($os_type eq 'MSWIN32') {
        $dir = "C:\\zabbix\\scripts";
    }
    if (!-d $dir) {
        make_path($dir);
    }
    return $dir;
}

sub parse_config_log {
    my $scripts_dir = check_dir();
    my $file_path = "$scripts_dir/zbx_logMonitor.conf";
    if (!-e $file_path) {
        open my $file, '>', $file_path;
        print $file "#tag;path;keyword;severity";
        close $file;
    }
    my @result;
    open my $f, '<', $file_path;
    while (<$f>) {
        chomp;
        next if /^$/ || /^#/;
        my ($tag, $path, $keyword, $level) = split ';';
        push @result, {
            "{#TAG}" => $tag,
            "{#PATH}" => $path,
            "{#KEYWORD}" => $keyword,
            "{#SEVERITY}" => uc $level
        };
    }
    close $f;
    print to_json(\@result, {pretty => 1});
}

sub parse_config_process {
    my $scripts_dir = check_dir();
    my $file_path = "$scripts_dir/zbx_processMonitor.conf";
    if (!-e $file_path) {
        open my $file, '>', $file_path;
        print $file "#tag;process;user;count;severity";
        close $file;
    }
    my @result;
    open my $f, '<', $file_path;
    while (<$f>) {
        chomp;
        next if /^$/ || /^#/;
        my ($tag, $process, $user, $count, $level) = split ';';
        $user = '' if $user eq '-';
        push @result, {
            "{#TAG}" => $tag,
            "{#PROCESS}" => $process,
            "{#USER}" => $user,
            "{#COUNT}" => $count,
            "{#SEVERITY}" => uc $level
        };
    }
    close $f;
    print to_json(\@result, {pretty => 1});
}

sub main {
    my $conf_type;
    GetOptions("conf_type|t=s" => \$conf_type);
    if ($conf_type eq 'log') {
        parse_config_log();
    } elsif ($conf_type eq 'process') {
        parse_config_process();
    } else {
        print "Usage: $0 --conf_type log|process\n";
        exit 1;
    }
}

main();
