FROM cimg/go:1.19

RUN go install "github.com/pschou/rpm-add-checksum@latest"

ENTRYPOINT [ "/home/circleci/go/bin/rpm-add-checksum" ]
CMD [ ]
