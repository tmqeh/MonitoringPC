USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Svr_Comm_Info_M]    Script Date: 2022-02-11 ¿ÀÀü 9:30:15 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Svr_Comm_Info_M](
	[hostName] [varchar](30) NOT NULL,
	[IPAddr] [varchar](15) NOT NULL,
	[ServerName] [varchar](100) NULL,
	[UseYN] [varchar](1) NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL,
 CONSTRAINT [PK_Svr_Comm_Info_M] PRIMARY KEY CLUSTERED 
(
	[hostName] ASC,
	[IPAddr] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


