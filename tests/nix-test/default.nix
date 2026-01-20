{
  pkgs,
  autolog,
  epnix,
  testers,
  lib,
  ...
}:
testers.runNixOSTest {
  name = "autolog-integration-test";

  node.pkgsReadOnly = false;
  nodes = {
    server = {pkgs, ...}: {
      imports = [epnix.nixosModules.nixos];

      services.phoebus-olog = {
        enable = true;
        settings."demo_auth.enabled" = true;
        settings."server.http.enable" = true;
      };

      services.elasticsearch = {
        enable = true;
        package = pkgs.elasticsearch7;
      };

      nixpkgs.config.allowUnfreePredicate = pkg:
        builtins.elem (lib.getName pkg) [
          # Elasticsearch can be used as an SSPL-licensed software, which is
          # not open-source. But as we're using it run tests, not exposing
          # any service, this should be fine.
          "elasticsearch"
        ];

      networking.firewall.allowedTCPPorts = [8181 8080];

      # Else phoebus-olog gets killed by the OOM killer
      virtualisation.memorySize = 2047;
    };

    client = {
      environment.systemPackages = [
        pkgs.gdb
        autolog
        pkgs.curl
        pkgs.epnix.epics-base
      ];
      systemd.tmpfiles.rules = [
        "f /tmp/test.txt 0644 root root - test"
      ];
      systemd.services = {
        ioc = {
          script = ''
            ${pkgs.epnix.epics-base}/bin/softIoc -d ${./iocs/test.db} -S
          '';
          wantedBy = ["multi-user.target"];
        };
        autolog = {
          script = ''
            ${autolog}/bin/autolog -v 1 ${./autolog-conf/test.toml} > "$STATE_DIRECTORY/autolog.log"
          '';
          serviceConfig = {
            StateDirectory = "autolog";
          };
          wantedBy = ["multi-user.target"];
        };
      };
    };
  };

  testScript = ''
    import json
    import time

    start_all()
    server.wait_for_unit("phoebus-olog.service")
    server.wait_for_open_port(8181)
    client.wait_for_unit("autolog.service")
    client.wait_for_unit("multi-user.target")
    with subtest("epics caget"):
      out = client.succeed("caget -t AUTOLOG-TEST:TRIGGER-LOG")
      print(repr(out))
      assert out.strip() == "5"

    client.wait_until_succeeds("caput AUTOLOG-TEST:TRIGGER-LOG 6")
    time.sleep(6)
    result = client.wait_until_succeeds("curl -X GET http://server:8080/Olog/logs?logbook=operations")
    time.sleep(4)
    print(result)
    with subtest("test log creation"):
      logs = json.loads(result)
      print(f"logs: {logs}")
      latest_log = logs[0]
      print(latest_log)
      assert latest_log["owner"] == "admin"
      assert latest_log["level"] == "info"
      assert latest_log["attachments"][0]["filename"] == "autolog.log"
      assert latest_log["title"] == "test title"
      assert  "test description" in latest_log["description"]
      assert "6" in latest_log["description"]
  '';
}
