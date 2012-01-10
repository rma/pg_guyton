library(rma.g92)




load("virtppl.4w.RData")
virtppl.4w$v_ISHYPER <- NULL
gc()

exp.count <- dim(virtppl.4w)[1]
ixs.pre <- seq(from = 1, to = exp.count, by = 2)
ixs.post <- seq(from = 2, to = exp.count, by = 2)

virtppl.pre <- virtppl.4w[ixs.pre,]

save(virtppl.pre, file = "virtppl.pre.RData", compress = "bzip2")
rm(virtppl.4w)
gc()




load("virtppl.1h.RData")
virtppl.1h.post <- virtppl.1h[ixs.post,]
rm(virtppl.1h)
gc()

virtppl.1h.ee <- interleave(virtppl.pre, virtppl.1h.post,
                            append.source=FALSE, sep="")
rm(virtppl.1h.post)
gc()

save(virtppl.1h.ee, file = "virtppl.1h.ee.RData", compress="bzip2")

ee.1h <- ElementaryEffects(virtppl.1h.ee)
save(ee.1h, file="virtppl.ee.1h.RData", compress="bzip2")

rm(virtppl.1h.ee, ee.1h)
gc()




load("virtppl.1m.RData")
virtppl.1m.post <- virtppl.1m[ixs.post,]
rm(virtppl.1m)
gc()

virtppl.1m.ee <- interleave(virtppl.pre, virtppl.1m.post,
                            append.source=FALSE, sep="")
rm(virtppl.1m.post)
gc()

save(virtppl.1m.ee, file = "virtppl.1m.ee.RData", compress="bzip2")

ee.1m <- ElementaryEffects(virtppl.1m.ee)
save(ee.1m, file="virtppl.ee.1m.RData", compress="bzip2")

rm(virtppl.1m.ee, ee.1m)
gc()




load("virtppl.1d.RData")
virtppl.1d.post <- virtppl.1d[ixs.post,]
rm(virtppl.1d)
gc()

virtppl.1d.ee <- interleave(virtppl.pre, virtppl.1d.post,
                            append.source=FALSE, sep="")
rm(virtppl.1d.post)
gc()

save(virtppl.1d.ee, file = "virtppl.1d.ee.RData", compress="bzip2")

ee.1d <- ElementaryEffects(virtppl.1d.ee)
save(ee.1d, file="virtppl.ee.1d.RData", compress="bzip2")

rm(virtppl.1d.ee, ee.1d)
gc()




load("virtppl.1w.RData")
virtppl.1w.post <- virtppl.1w[ixs.post,]
rm(virtppl.1w)
gc()

virtppl.1w.ee <- interleave(virtppl.pre, virtppl.1w.post,
                            append.source=FALSE, sep="")
rm(virtppl.1w.post)
gc()

save(virtppl.1w.ee, file = "virtppl.1w.ee.RData", compress="bzip2")

ee.1w <- ElementaryEffects(virtppl.1w.ee)
save(ee.1w, file="virtppl.ee.1w.RData", compress="bzip2")

rm(virtppl.1w.ee, ee.1w)
gc()




load("virtppl.4w.RData")

virtppl.4w.ee <- virtppl.4w
gc()

save(virtppl.4w.ee, file = "virtppl.4w.ee.RData", compress="bzip2")

ee.4w <- ElementaryEffects(virtppl.4w.ee)
save(ee.4w, file="virtppl.ee.4w.RData", compress="bzip2")

rm(virtppl.4w.ee, ee.4w)
gc()




load("virtppl.1m.ee.RData")
load("virtppl.1h.ee.RData")
load("virtppl.1d.ee.RData")
load("virtppl.1w.ee.RData")
load("virtppl.4w.ee.RData")

ee.list <- list(ee.4w=ee.4w, ee.1w=ee.1w, ee.1d=ee.1d, ee.1h=ee.1h,
                ee.1m=ee.1m)
save(ee.list, file="virtppl.ee.RData", compress="bzip2")
